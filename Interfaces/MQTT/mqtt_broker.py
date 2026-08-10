from .MQTT_Client import mqtt_client
from credentials import mqtt_broker_address,mqtt_broker_port
import json

broker_address = mqtt_broker_address
broker_port    = mqtt_broker_port

with open("./confluence_config.json",'r') as fid:
    configs = json.load(fid)
node = configs['Node Name']

broker = mqtt_client(broker_address,broker_port,subscriptions=[f"{node}/#"])
