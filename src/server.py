#!//usr/bin/env python
import subprocess
from database_connection import DatabaseConnection
import json
import sys
from flask import Flask,request,send_file,abort,Response
import argparse
import io
import re
import random
import cmd2web
import os
import settings
from OpenSSL import SSL
from flask_cors import CORS, cross_origin
from pathlib import Path

app = Flask(__name__)
CORS(app)
config = None
server = None
timeout=10
apache_server = False


current_directory= os.path.dirname(__file__)
apache_config_file_path=os.path.join(current_directory, '../ex_configs/apache_conf.yaml')
apache_file = Path(apache_config_file_path)
if apache_file.is_file():
    apache_server = True
else:
    apache_server = False
'''Get the boolean value for apache server'''

add_accesss_control = True
# myenvvar = os.environ["my_config_file"]
# sys.stderr.write("hello there from my CGI script.{0}\n".format(myenvvar))
@app.after_request
def after_request(response):
    if add_accesss_control:
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/info')
def info():
    sys.stderr.write("hello there from info method my CGI script.======={0}=======\n".format(server))
    return json.dumps(server.get_info())

@app.route('/')
def service():
    #Note: Add the path to the settings file
    database_file_path = os.path.join(current_directory, "../DBScript/CMD2WEB.sqlite")
    database_object = DatabaseConnection(database_file_path)

    service = request.args.get('service')

    if not service:
        return cmd2web.Server.error('No service specified')

    if not server.has_service(service):
        return cmd2web.Server.error('Unknown service')

    if not server.services[service].args_match(request.args):
        return cmd2web.Server.error('Argument mismatch')

    service_instance = server.services[service].copy()
    sys.stderr.write("\n\n\nService Instance: {0}\n\n\n".format(service_instance))
    if(hasattr(service_instance, 'group')):
        restricted = database_object.get_restricted_access(service_instance.group)
        if(restricted == True):
            #Check if token is present in parameter
            token = request.args.get('token');
            if not token:
                return cmd2web.Server.error('Access restricted without token.')
            token_access = database_object.check_token_access(service_instance.group,token)
            if(token_access == True):
                return process_service(service_instance)
            else:
                return cmd2web.Server.error('Wrong or expired token. Access Denied')
        else:
            return process_service(service_instance)
    else:
        return process_service(service_instance)

##################Extra for Apache server - start#############

def process_service(service_instance):
    try:
        cmd = service_instance.make_cmd(request.args)
    except Exception as e:
        return cmd2web.Server.error(str(e))

    # print(' '.join(cmd))

    out_file_name = '/tmp/' + str(random.randint(0,sys.maxsize)) + '.out'
    f = open(out_file_name, 'w')
    try:
        proc = subprocess.check_call(cmd,
                                     stderr=None,
                                     stdout=f,
                                     timeout=timeout)
        sys.stderr.write("\n\n\Command: {0}\n\n\n".format(cmd))
        # res = subprocess.check_output(cmd,stderr=sys.stderr)
        # sys.stderr.write("\n\n\nResult: {0}\n\n\n".format(res))
    except subprocess.TimeoutExpired as e:
        print('Time Out')
        return cmd2web.Server.error('Time limit for current request exceed.')
    except Exception as e:
        return cmd2web.Server.error(str(e))

    f.close()
    sys.stderr.write("\n\n\nOut file name after processing: {0}\n\n\n".format(out_file_name))
    return service_instance.process_result(out_file_name)

def apache_conf():
    external_server = settings.Settings(type= "External_Server",filepath = apache_config_file_path)
    sys.stderr.write("hello external_server from my CGI script-----{0}----\n".format(external_server))
    if(external_server):
        args = settings.Settings(type= "Default_Apache_Conf",filepath = apache_config_file_path)
        timeout = args['Timeout']
        sys.stderr.write("hello there from inside main method my CGI script.===={0}==={1}===={2}===\n".format(timeout,args['Default_Config_File'],args['No_Access_Control_Header']))
        server = cmd2web.Server.load(args['Default_Config_File'])
        if args['No_Access_Control_Header']:
            add_accesss_control = False
        return server
    
if(apache_server):
    #Setting config object for the apache server.
    server = apache_conf()
##################Extra for Apache server - end#############


if __name__ == '__main__':
    sys.stderr.write("hello there from inside main method my CGI script.==============\n")
    parser = argparse.ArgumentParser(description='command to web server.')

    # parser.add_argument('--config',
    #                     dest='config',
    #                     required=True,
    #                     help='Configuration file.')
    parser.add_argument('--config',
                        dest='config',
                        required=True,
                        help='Configuration file.')

    parser.add_argument('--port',
                        dest='port',
                        type=int,
                        default="8080",
                        help='Port to run on (default 8080)')

    parser.add_argument('--host',
                        dest='host',
                        default="127.0.0.1",
                        help='Server hos (default 127.0.0.1)')

    parser.add_argument('--timeout',
                        dest='timeout',
                        type=int,
                        default=10,
                        help='Max runtime (sec) for a command (default 10)')

    parser.add_argument('--ssl_key',
                        dest='ssl_key',
                        help='Path to the SSL key')

    parser.add_argument('--ssl_cert',
                        dest='ssl_cert',
                        help='Path to the SSL key')

    parser.add_argument('--no_access_control_header',
                        dest='no_access_control_header',
                        action='store_true',
                        help='Path to the SSL key')

    args = parser.parse_args()
    timeout = args.timeout
    # app.logger.info('testing info log'+args.config)
    server = cmd2web.Server.load(args.config)
    # server = cmd2web.Server.load('../ex_configs/example_config.yaml')

    if args.no_access_control_header:
        add_accesss_control = False


    if args.ssl_key and args.ssl_cert:
        context = SSL.Context(SSL.SSLv23_METHOD)
        context.use_privatekey_file('yourserver.key')
        context.use_certificate_file('yourserver.crt')
        try:
            app.run(host=args.host, port=args.port, ssl_context=context)
        except Exception as e:
            sys.exit('ERROR starting the server. "' + str(e) + '"')
    else:
        try:
            app.run(host=args.host, port=args.port)
        except Exception as e:
            sys.exit('ERROR starting the server. "' + str(e) + '"')
