from .Fuji_VFD_funcs import VFD
import json
from Interfaces.MQTT import broker
import pandas as pd
from Interfaces.Scheduler import scheduler

with open("./confluence_config.json",'r') as fid:
    configs = json.load(fid)

# Pull out a few commonly used parameters from the config file
node = configs['Node Name']
interface = "Fuji_Frenic_VFD"
comms_configs = configs[interface]['comms']
publish_configs = configs[interface]['publish']

# instantiate the VFD object and open the com port to establish communication with the device.
frenic_vfd = VFD(
    comm_port =comms_configs['com port'],
    server_id =comms_configs['serverID'],
    baudrate  =comms_configs['baudrate'],
    bytesize  =comms_configs['bytesize'],
    parity    =comms_configs['parity'],
    stopbits  =comms_configs['stopbits'],
    timeout   =comms_configs['timeout']
)

def on_frenic_message(client,userdata,message):
    print(f"Messaged Received on Topic:{message.topic}.  Message: {message.payload.decode()}")
    subtopic = message.topic.split('/')[-1] # get the final subtopic of the message.

    # start_motor/stop_motor/clear_faults/send_setpoint now raise on a
    # Modbus comm failure (previously swallowed silently) so the
    # request/reply handler below can report a real ok:False — this
    # legacy paho message_callback_add path has no exception boundary of
    # its own, so a comm failure here needs to be caught explicitly
    # rather than escaping into paho's message-dispatch thread, which
    # would otherwise die silently and stop processing MQTT messages
    # entirely (no systemd restart, since the process itself keeps running).
    try:
        if subtopic == "send_setpoint":
            print('\n\n Send Setpoint Command Received!\n\n')
            frenic_vfd.send_setpoint(message.payload)
        elif subtopic == "start_motor":
            frenic_vfd.start_motor()
        elif subtopic == "stop_motor":
            frenic_vfd.stop_motor()
        elif subtopic == "clear_faults":
            frenic_vfd.clear_faults()
    except Exception as e:
        print(f"Fuji_Frenic_VFD: legacy command {subtopic!r} failed: {e}")

broker.client.message_callback_add(f"{node}/{interface}/commands/#",on_frenic_message)

# Request/reply command handling for laguna's MQTT transport (see
# laguna.mqtt.request_reply): laguna publishes a JSON envelope
# {"request_id", "command", "args"} on the exact "{node}/{interface}/commands"
# topic (not a "/commands/<subtopic>" wildcard like on_frenic_message above)
# and blocks for a reply on "{node}/{interface}/replies" echoing the same
# request_id. This is additive — the legacy subtopic handler above is
# untouched for any other existing publisher.
_COMMAND_HANDLERS = {
    "set_setpoint_hz": lambda args: frenic_vfd.send_setpoint(args["freq_hz"]),
    "start_motor": lambda args: frenic_vfd.start_motor(),
    "stop_motor": lambda args: frenic_vfd.stop_motor(),
    "clear_faults": lambda args: frenic_vfd.clear_faults(),
}

def on_frenic_request(client, userdata, message):
    try:
        envelope = json.loads(message.payload)
        request_id = envelope["request_id"]
        command = envelope["command"]
        args = envelope.get("args", {})
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Fuji_Frenic_VFD: malformed request envelope: {e}")
        return

    handler = _COMMAND_HANDLERS.get(command)
    if handler is None:
        print(f"Fuji_Frenic_VFD: unknown command {command!r}")
        broker.publish_message(
            topic=f"{node}/{interface}/replies",
            payload=json.dumps({"request_id": request_id, "ok": False}),
        )
        return

    try:
        handler(args)
        ok = True
    except Exception as e:
        print(f"Fuji_Frenic_VFD: command {command!r} failed: {e}")
        ok = False

    broker.publish_message(
        topic=f"{node}/{interface}/replies",
        payload=json.dumps({"request_id": request_id, "ok": ok}),
    )

broker.client.message_callback_add(f"{node}/{interface}/commands", on_frenic_request)

def task():
    """
    This function is the task that will be called each time the scheduled job is executed. 
    This function handle is the value that should be entered for the "func" parameter of scheduler.add_job()

    Arguments: 
    none

    Returns:
    none
    """
    frenic_vfd.poll_status()

    broker.publish_message(topic=f"{node}/{interface}",payload=pd.Series(frenic_vfd.status).to_json())
    # print(pd.Series(frenic_vfd.status).to_json())

if publish_configs['type'] == 'cron':
    job_configuration = {
        "func":task,
        "args":[],
        "trigger":"cron",
        "hour":publish_configs['interval_hr'],
        "minute":publish_configs['interval_min'],
        "second":publish_configs['interval_sec'],
        "id":"frenic_vfd"
    }
elif publish_configs['type'] =='interval':
        job_configuration = {
        "func":task,
        "args":[],
        "trigger":"interval",
        "seconds":publish_configs['seconds'],
        "id":"frenic_vfd"
    }


scheduler.add_job(**job_configuration)