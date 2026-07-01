import paho.mqtt.client as mqtt
import json
import datetime

class mqtt_client():
    def __init__(self,broker_address,broker_port,subscriptions):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self.on_message
        try:
            self.client.connect(broker_address,broker_port,keepalive=60)
        except TimeoutError:
            print(f'Unable to connect to MQTT broker at {broker_address}:{broker_port}')
        for sub in subscriptions:
            self.client.subscribe(sub)

        self.client.loop_start()

        self.data = {}
        self.scan_data = {}

        self.time_of_last_status = 'No Data Recieved Yet'
        self.counter = 0

    def on_message(self,client,userdata,msg):
        self.data[msg.topic] = {}
        # print(msg.topic)
        self.time_of_last_message = datetime.datetime.now()
        msg_dict = json.loads(msg.payload.decode('utf-8'))

    def publish_message(self,topic,payload):
        self.client.publish(topic=topic,payload=payload)