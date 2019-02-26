import os
import yaml
import sys

class Settings():
    def __new__(self, type=None, filepath=None):
        try:
            current_directory= os.path.dirname(__file__)
            complete_file_path=os.path.join(current_directory, filepath)
            f = open(complete_file_path, 'r')
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


