import json
import time
import datetime
import hashlib
import os

class configs_monitor():
    def __init__(self):
        self.file_path = "./confluence_config.json"
        self.last_hash  = self.get_file_hash()
        self.last_mod_time = os.path.getmtime(self.file_path)

    def get_file_hash(self):
        hasher = hashlib.sha256()
        with open(self.file_path, "rb") as f:
            # Read in chunks to efficiently handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
        # self.new_hash = hasher.hexdigest()

    def config_file_changed(self):
        print(f"{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Checking Config File for Changes ")
        new_mod_time = os.path.getmtime(self.file_path)
        if new_mod_time != self.last_mod_time:
            # Check the hash to make sure it changed: 
            new_hash = self.get_file_hash()
            # print(f"Last Hash: {self.last_hash}")
            # print(f"This Hash: {new_hash}")
            if new_hash != self.last_hash:
                # print('The config file has changed!')
                self.last_hash = new_hash
                self.last_mod_time = new_mod_time
                # print(datetime.datetime.now())
                # print("Configs File Changed!")
                return True
        else:
            # print(datetime.datetime.now())
            # print("Configs File is the Same")
            return False