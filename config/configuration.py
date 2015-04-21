import json
import os

class Configuration:

    config = None

    @staticmethod
    def init():
        '''
        Initialize static variable config by reading config.json. All parameters are defined in this file,
        and will persist changes.
        '''
        try:
            json_data = open('config.json')
            Configuration.config = json.load(json_data)
            json_data.close()
        except:
            raise RuntimeError("Cant open config file")



    @staticmethod
    def get():
        '''
        Method returns configurations. If not loaded calls init()
        '''
        if not Configuration.config:
            Configuration.init()
        return Configuration.config

    @staticmethod
    def reload():
        Configuration.init()

    @staticmethod
    def store(config):
        '''
        If changes has been made to config.json through the GUI, the changes is persisted by calling
        store with the new configuration. The argument should have the same structure as config.json.
        Only key value pairs define inside a parameters dict, is persisted.
        '''
        json_data = open('config.json', 'w')
        data = Configuration.config
        p = "parameters"
        for module in data.keys():
            for element in data[module].keys():
                if p in data[module][element]:
                    for a in data[module][element][p].keys():
                        data[module][element][p][a] = config[module][element][p][a]
        json_data.seek(0)
        json.dump(data, json_data, indent=4)
        json_data.close()