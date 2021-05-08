import configparser

config = configparser.ConfigParser(allow_no_value=True)

config["DEFAULT"] = {"Search Method": "PIN",
                     "Age Range": "18-44", "Calendar View": True}

config["PIN CODES"] = {"400614": None, "400706": None, "400703": None}

with open('config.ini', 'w') as configfile:
    config.write(configfile)
