import json
from Interfaces.MQTT import broker
import pandas as pd
from Interfaces.Scheduler import scheduler
from .NodeStats_funcs import get_cpu_usage, get_cpu_temperature,get_ram_metrics,get_disk_metrics,NetworkTracker
import datetime

with open("./confluence_config.json",'r') as fid:
    configs = json.load(fid)

# Pull out a few commonly used parameters from the config file
node = configs['Node Name']
interface = 'NodeStats'
publish_configs = configs[interface]['publish']


# instantiate the network tracker. 
net_tracker = NetworkTracker()

def task():
    """
    This function is the task that will be called each time the scheduled job is executed. 
    This function handle is the value that should be entered for the "func" parameter of scheduler.add_job()

    Arguments: 
    none

    Returns:
    none
    """

    cpu_usage = get_cpu_usage(interval=1)
    cpu_temp  = get_cpu_temperature()
    ram = get_ram_metrics()
    disk = get_disk_metrics()
    net = net_tracker.get_speeds()


    cpu_stats = {"timestamp":datetime.datetime.now().isoformat(timespec='milliseconds'),
                 'RAM':f"{ram['percent']}% ({ram['used_gb']:.2f} GB / {ram['total_gb']:.2f} GB)",
                 "DISK": f"{disk['percent']}% ({disk['used_gb']:.2f} GB / {disk['total_gb']:.2f} GB)",
                 'CPU Usage':f'{cpu_usage} %',
                 'CPU Temp':f"{cpu_temp} degC",
                 "NET": f"Down: {net['download']} | Up: {net['upload']}"
    }
    

    broker.publish_message(topic=f"{node}/{interface}",payload=pd.Series(cpu_stats).to_json())

if publish_configs['type'] == 'cron':
    job_configuration = {
        "func":task,
        "args":[],
        "trigger":"cron",
        "hour":publish_configs['interval_hr'],
        "minute":publish_configs['interval_min'],
        "second":publish_configs['interval_sec'],
        "id":"NodeStats"
    }
elif publish_configs['type'] =='interval':
        job_configuration = {
        "func":task,
        "args":[],
        "trigger":"interval",
        "seconds":publish_configs['seconds'],
        "id":"NodeStats"
    }


scheduler.add_job(**job_configuration)