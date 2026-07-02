import Massa_Ultrasonic
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED
import time
# import importlib

scheduler = BlockingScheduler()
config_file_path = './confluence_config.json'

def schedule_jobs():
    with open(config_file_path,'r') as fid:
        configs = json.load(fid)
    
    node = configs['Node Name']
    active_interfaces = [interface.lower() for interface in configs['Active Interfaces']]


    # Add other jobs
    if len([string for string in active_interfaces if 'massa' in string.lower()]) >0: # if any of the active interfaces have the word "massa" in them
        scheduler.add_job(**Massa_Ultrasonic.job_configuration)


    try:
        print("APScheduler started with parameterized jobs...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Shutting Down APScheduler")


if __name__ == "__main__":
    schedule_jobs()
    



