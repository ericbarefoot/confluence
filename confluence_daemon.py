import Massa_Ultrasonic
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED
import config_file_funcs
import time

scheduler = BlockingScheduler()
config_file_path = './confluence_config.json'

def job_listener(event):
    if event.job_id == "Config mod monitor":
        if event.retval == True:
            print(f"The Config JSON File changed. Stopping All Jobs")
            # scheduler.remove_job(event.job_id)
            scheduler.remove_all_jobs()
            scheduler.shutdown(wait=False)

            time.sleep(1)

            print('Rescheduling jobs with new config JSON')
            print(Massa_Ultrasonic.job_config.job_configuration)
            # schedule_jobs()

def schedule_jobs():
    with open(config_file_path,'r') as fid:
        configs = json.load(fid)
    
    node = list(configs.keys())[0]
    active_interfaces = [interface.lower() for interface in configs[node]['Active Interfaces']]

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
    if len([string for string in active_interfaces if 'massa' in string.lower()]) >0: # if any of the active interfaces have the word "massa" in them
        scheduler.add_job(**Massa_Ultrasonic.job_configuration)

    scheduler.add_listener(job_listener,EVENT_JOB_EXECUTED)

    try:
        print("APScheduler started with parameterized jobs...")
        scheduler.start()
    # except Exception as e:
    #     print(e)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    schedule_jobs()
    print("Shutting Down APScheduler")



