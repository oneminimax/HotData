import configparser

config = configparser.ConfigParser()
config.read('HotDataConfig.ini')

print(config['Param']['default_data_path'])