from .Teknic_ClearCore_funcs import TeknicClearCore
import json
from Interfaces.MQTT import broker
from Interfaces.Scheduler import scheduler

with open("./confluence_config.json",'r') as fid:
    configs = json.load(fid)

# Pull out a few commonly used parameters from the config file
node = configs['Node Name']
interface = 'Teknic_ClearCore'
comms_configs = configs[interface]['comms']
publish_configs = configs[interface]['publish']

# One physical ClearCore drives both the weir gate axis and the flow
# valve digital IO — see Teknic_ClearCore_funcs.py's module docstring.
clearcore = TeknicClearCore(comm_port=comms_configs['com port'], baudrate=comms_configs['baudrate'])

# Request/reply command handling for laguna's MQTT transport (see
# laguna.mqtt.request_reply): laguna publishes a JSON envelope
# {"request_id", "command", "args"} on "{node}/weir/commands" /
# "{node}/flow_valve/commands" and blocks for a reply on the matching
# ".../replies" topic echoing the same request_id.

def on_weir_command(client, userdata, message):
    try:
        envelope = json.loads(message.payload)
        request_id = envelope["request_id"]
        command = envelope["command"]
        args = envelope.get("args", {})
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Teknic_ClearCore (weir): malformed request envelope: {e}")
        return

    try:
        reply = clearcore.handle_weir_command(command, args)
    except Exception as e:
        # handle_weir_command() itself doesn't catch a comm failure from the
        # underlying TeknicMotor call (several of its methods raise directly
        # rather than swallowing) — this callback has no exception boundary
        # of its own otherwise, and an uncaught exception here would escape
        # into paho's message-dispatch thread, silently killing MQTT message
        # processing for the whole node rather than just this command
        # failing (see the equivalent fix in Fuji_Frenic_VFD/job_config.py's
        # on_frenic_request).
        print(f"Teknic_ClearCore (weir): command {command!r} failed: {e}")
        reply = {"ok": False, "error": str(e)}
    reply["request_id"] = request_id
    broker.publish_message(topic=f"{node}/weir/replies", payload=json.dumps(reply))


def on_flow_valve_command(client, userdata, message):
    try:
        envelope = json.loads(message.payload)
        request_id = envelope["request_id"]
        command = envelope["command"]
        args = envelope.get("args", {})
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Teknic_ClearCore (flow_valve): malformed request envelope: {e}")
        return

    try:
        reply = clearcore.handle_valve_command(command, args)
    except Exception as e:
        print(f"Teknic_ClearCore (flow_valve): command {command!r} failed: {e}")
        reply = {"ok": False, "error": str(e)}
    reply["request_id"] = request_id
    broker.publish_message(topic=f"{node}/flow_valve/replies", payload=json.dumps(reply))


broker.client.message_callback_add(f"{node}/weir/commands", on_weir_command)
broker.client.message_callback_add(f"{node}/flow_valve/commands", on_flow_valve_command)


def task():
    """
    This function is the task that will be called each time the scheduled job is executed.
    This function handle is the value that should be entered for the "func" parameter of scheduler.add_job()

    Arguments:
    none

    Returns:
    none
    """
    clearcore.poll_weir_status()
    clearcore.poll_valve_status()
    broker.publish_message(topic=f"{node}/weir", payload=json.dumps(clearcore.weir_status))
    broker.publish_message(topic=f"{node}/flow_valve", payload=json.dumps(clearcore.valve_status))

if publish_configs['type'] == 'cron':
    job_configuration = {
        "func":task,
        "args":[],
        "trigger":"cron",
        "hour":publish_configs['interval_hr'],
        "minute":publish_configs['interval_min'],
        "second":publish_configs['interval_sec'],
        "id":"Teknic_ClearCore"
    }
elif publish_configs['type'] =='interval':
        job_configuration = {
        "func":task,
        "args":[],
        "trigger":"interval",
        "seconds":publish_configs['seconds'],
        "id":"Teknic_ClearCore"
    }


scheduler.add_job(**job_configuration)
