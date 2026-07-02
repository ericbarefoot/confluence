from .Massa_funcs import massa
import json
from Interfaces.MQTT import broker
import pandas as pd

with open("./confluence_config.json",'r') as fid:
    configs = json.load(fid)

# Pull out a few commonly used parameters from the config file
node = configs['Node Name']
interface = [string for string in list(configs.keys()) if 'massa' in string.lower()][0]
comms_configs = configs[interface]['comms']
publish_configs = configs[interface]['publish']

# instantiate the massa objects.  Open the comm port to establish communication with the devices.
massas = massa(comm_port=comms_configs['com port'],ids=comms_configs["ids"],names=configs[interface]['device names'],offset_array=configs[interface]["offsets_mm"])

def task():
    """
    This function is the task that will be called each time the scheduled job is executed. 
    This function handle is the value that should be entered for the "func" parameter of scheduler.add_job()

    Parameters: 
    none

    Returns:
    none
    """
    massas.poll_status()
    broker.publish_message(topic=f"{node}/{interface}",payload=pd.Series(massas.status).to_json())
    print(pd.Series(massas.status).to_json()) # Using the pandas to_json instead of json.dumps handles converting to NAN to null.  JSON format doesn't support NANs.

job_configuration = {
    "func":task,
    "args":[],
    "trigger":"cron",
    "hour":publish_configs['interval_hr'],
    "minute":publish_configs['interval_min'],
    "second":publish_configs['interval_sec'],
    "id":"Massa RS-485"
}