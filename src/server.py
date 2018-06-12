#!//usr/bin/env python
import subprocess
import json
import sys
from flask import Flask,request,send_file,abort,Response
import argparse
import io
import re
import random
import cmd2web

app = Flask(__name__)

config = None
server = None
timeout=10

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/info')
def info():
    return json.dumps(server.get_info())

@app.route('/')
def service():

    service = request.args.get('service')

    if not service:
        return cmd2web.Server.error('No service specified')

    if not server.has_service(service):
        return cmd2web.Server.error('Unknown service')

    if not server.services[service].args_match(request.args):
        return cmd2web.Server.error('Argument mismatch')

    service_instance = server.services[service].copy()
    
    try:
        cmd = service_instance.make_cmd(request.args)
    except Exception as e:
        return cmd2web.Server.error(str(e))

    out_file_name = '/tmp/' + str(random.randint(0,sys.maxsize)) + '.out'

    f = open(out_file_name, 'w')

    try:
        proc = subprocess.check_call(cmd,
                                     stderr=sys.stderr,
                                     stdout=f,
                                     timeout=timeout)
    except subprocess.TimeoutExpired as e:
        print('Time Out')
        return cmd2web.Server.error('Time limit for current request exceed.')
    except Exception as e:
        return cmd2web.Server.error(str(e))

    f.close()

    return service_instance.process_result(out_file_name)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='command to web server.')

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


    args = parser.parse_args()
    timeout = args.timeout
    server = cmd2web.Server.load(args.config)
    try:
        app.run(host=args.host, port=args.port)
    except Exception as e:
        sys.exit('ERROR starting the server. "' + str(e) + '"')
