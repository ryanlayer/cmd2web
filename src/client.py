import cmd2web
import os
from pathlib import Path
apache_server = False


current_directory= os.path.dirname(__file__)
apache_config_file_path=os.path.join(current_directory, '../ex_configs/apache_conf.yaml')
apache_file = Path(apache_config_file_path)
if apache_file.is_file():
    apache_server = True
else:
    apache_server = False

if(apache_server):
    s = cmd2web.Client.connect('http://localhost/cmd2web')
else:
    s = cmd2web.Client.connect('http://127.0.0.1:8080')

try:
    R = s.run('simpleGrep',
              pattern='zip')

except Exception as e:
    print(str(e))

print(R)
