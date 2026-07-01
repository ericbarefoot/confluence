from .Massa_funcs import massa
import json
from MQTT import broker

with open("./confluence_config.json",'r') as fid:
    configs = json.load(fid)

node = list(configs.keys())[0]

print(configs[node].keys())

interface = [string for string in list(configs[node].keys()) if 'massa' in string.lower()][0]

comms_configs = configs[node][interface]['comms']
publish_configs = configs[node][interface]['publish']

massas = massa(comms_configs['com port'],comms_configs["ids"],comms_configs["offsets_mm"])

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