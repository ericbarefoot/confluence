from .MQTT_Client import mqtt_client
from credentials import mqtt_broker_address,mqtt_broker_port

broker_address = mqtt_broker_address
broker_port    = mqtt_broker_port

broker = mqtt_client(broker_address,broker_port,subscriptions=[])