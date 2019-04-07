import json
from PyExpUtils.utils.fp import once

class Config:
    def __init__(self):
        with open('config.json', 'r') as f:
            d = json.load(f)

        self.save_path = d['save_path']
        self.log_path = d.get('log_path', '.logs')
        self.experiment_directory = d.get('experiment_directory', 'experiments')

@once
def getConfig():
    return Config()
