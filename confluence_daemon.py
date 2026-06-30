import Massa_funcs
import json
import time
import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED
import config_file_funcs
import MQTT_Client

scheduler = BlockingScheduler()
config_file_path = './confluence_config.json'

broker_address = '160.94.187.160'
broker_port    = 1883
mqtt = MQTT_Client.mqtt_client(broker_address,broker_port,subscriptions=[])

def job_listener(event):
    if event.job_id == "Config mod monitor":
        if event.retval == True:
            print(f"The Config JSON File changed. Stopping All Jobs")
            # scheduler.remove_job(event.job_id)
            scheduler.remove_all_jobs()
            scheduler.shutdown(wait=False)
            # print(scheduler.state)
    elif event.job_id == "Massa RS-485":
        print('Massa JSON:')
        print(event.retval)
        with open(config_file_path,'r') as fid:
            configs = json.load(fid)
    
        node = list(configs.keys())[0]
        active_interfaces = configs[node]["Active Interfaces"]
        print(f"{node}/Massa RS-485")
        mqtt.publish_message(topic=f"{node}/Massa RS-485",payload=json.dumps(event.retval))

def schedule_jobs():
    with open(config_file_path,'r') as fid:
        configs = json.load(fid)
    
    node = list(configs.keys())[0]
    active_interfaces = configs[node]["Active Interfaces"]

    # start by scheduling the configs monitoring
    config_monitor = config_file_funcs.configs_monitor()
    scheduler.add_job(
        config_monitor.config_file_changed,
        # args=[config_last_modified,last_hash],
        trigger='cron',
        minute= '*',
        second='*/1',
        id="Config mod monitor"
    )

    # Add other jobs
    for i in active_interfaces:
        if i == "Massa RS-485":
            massas = Massa_funcs.massa(
                configs[node]['Massa RS-485']['comms']['com port'],
                configs[node]['Massa RS-485']['comms']['ids'],
                configs[node]['Massa RS-485']['comms']['offsets_mm']
                )
            
            massa_interval = [
                configs[node]['Massa RS-485']['publish']['interval_hr'],
                configs[node]['Massa RS-485']['publish']['interval_min'],
                configs[node]['Massa RS-485']['publish']['interval_sec']
            ]

            for j,dt in enumerate(massa_interval):
                if dt == 0:
                    massa_interval[j] = '*'
                else:
                    massa_interval[j] = "*/"+str(dt)
            # print(interval)

            scheduler.add_job(
                massas.poll_status,
                trigger='cron',
                hour = massa_interval[0],
                minute=massa_interval[1],
                second=massa_interval[2],
                id="Massa RS-485"
            )

    scheduler.add_listener(job_listener,EVENT_JOB_EXECUTED)

    try:
        print("APScheduler started with parameterized jobs...")
        scheduler.start()
    # except Exception as e:
    #     print(e)
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    schedule_jobs()



