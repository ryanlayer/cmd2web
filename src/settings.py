import os
import yaml
import sys

class Settings():
    def __new__(self, type=None, filepath=None):
        try:
            f = open(filepath, 'r')
            self.all_file = yaml.safe_load(f)
            f.close()
        except Exception as e:
            sys.exit('ERROR loading config file. "' + str(e) + '"')
        try:
            if type:
                self.settings = self.all_file[type]
            else:
                self.settings = self.all_file
            return self.settings
        except Exception as e:
            sys.exit('ERROR processing config file. "' + str(e) + '"')


