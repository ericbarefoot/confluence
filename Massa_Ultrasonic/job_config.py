from .Massa_funcs import massa
import json
from MQTT import broker

with open("./confluence_config.json",'r') as fid:
    configs = json.load(fid)

node = configs['Node Name']
interface = [string for string in list(configs.keys()) if 'massa' in string.lower()][0]

comms_configs = configs[interface]['comms']
publish_configs = configs[interface]['publish']

massas = massa(comm_port=comms_configs['com port'],ids=comms_configs["ids"],names=configs[interface]['device names'],offset_array=configs[interface]["offsets_mm"])

def task():
    massas.poll_status()
    broker.publish_message(topic=f"{node}/{interface}",payload=json.dumps(massas.status))
    print(json.dumps(massas.status))

job_configuration = {
    "func":task,
    "args":[],
    "trigger":"cron",
    "hour":publish_configs['interval_hr'],
    "minute":publish_configs['interval_min'],
    "second":publish_configs['interval_sec'],
    "id":"Massa RS-485"
}