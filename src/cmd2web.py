
import json
import sys
import re
import random
from flask import Flask,send_file
import requests
import logging
import settings
from logtest import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
#{{{def test_required(name, required, config):
def test_required(name, required, config):
    for r in required:
        if r not in config:
            sys.exit('ERROR in ' + name + ' definition. "' + r + \
                     '" not defined.')
#}}}

#{{{class Argument:
class Argument:
    
    #{{{
    @staticmethod
    def type_check(test_value, type):
        if type == 'string':
            return True

        elif type == 'integer':
            try:
                int(test_value)
            except ValueError:
                return False
            return True

        elif type == 'float':
            try:
                float(test_value)
            except ValueError:
                return False
            return True
        return False

    #}}}

    #{{{def load(config):
    @staticmethod
    def load(config):
        required = ['name', 'type', 'fixed']
        test_required('argument', required, config)

        if config['fixed'] not in ['true', 'false']:
            sys.exit('ERROR in argument definition. "' + \
                     config['fixed'] + '" is not a valid value for fixed.') 

        fixed = False
        value = None
        if config['fixed'] == 'true':
            required = ['value']
            test_required('argument', required, config)
            value = config['value']
            fixed = True


        if config['type'] not in ['string', 'integer', 'float']:
            sys.exit('ERROR in argument definition. Type "' + \
                     config['type'] + \
                     '" is not supported.')

        return Argument(config['name'],
                        config['type'],
                        fixed,
                        value)
                        
    #}}}

    #{{{ def __init__(self, name, dtype, fixed, value):
    def __init__(self, name, dtype, fixed, value):

        self.name = name

        if dtype not in ['string', 'integer', 'float']:
            sys.exit('ERROR in argument definition. Type "' + \
                     dtype + \
                     '" is not supported.')

        self.fixed = fixed
        self.value = value
        self.type = dtype
    #}}}

    #{{{def __str__(self):
    def __str__(self):
        return ' '.join([ 'name:' + self.name,
                          'fixed:' + str(self.fixed),
                          'value:' + str(self.value),
                          'type:' + str(self.type) ])
    #}}}

    #{{{def get_info(self):
    def get_info(self):
        if self.fixed:
            return None

        argument_info = {}
        argument_info['name'] = self.name
        argument_info['type'] = self.type

        return argument_info
    #}}}

    #{{{def copy(self):
    def copy(self):
        return Argument(self.name, self.type, self.fixed, self.value)
    #}}}

    #{{{ def type_test(self, test_value):
    def type_test(self, test_value):
        return Argument.type_check(test_value, self.type)
#        if self.type == 'string':
#            return True
#
#        elif self.type == 'integer':
#            try:
#                int(test_value)
#            except ValueError:
#                return False
#            return True
#
#        elif self.type == 'float':
#            try:
#                float(test_value)
#            except ValueError:
#                return False
#            return True
#        return False
    #}}}
#}}}

#{{{class Output:
class Output:
    #{{{def load(config):
    @staticmethod
    def load(config):
        required = ['type']
        test_required('output', required, config)

        supported_types = ['text_stream', 'file']

        otype = config['type']
        if otype not in supported_types:
            sys.exit('ERROR in output definition. "' + otype + \
                     '" is not a supported type (' + \
                     ' '.join(supported_types) + ')')

        if otype == 'text_stream':
            sep = '\t'
            if 'sep' in config:
                sep = config['sep']
            return Output(otype, sep=sep)

        if otype == 'file':
            required = ['value', 'mimetype']
            test_required('output file', required, config)
            value = config['value']  
            mimetype = config['mimetype']  
            return Output(otype, value=value, mimetype=mimetype)
    #}}}
                    
    #{{{def __init__(self, otype, value=None, mimetype=None, sep=None):
    def __init__(self, otype, value=None, mimetype=None, sep=None):
        self.type = otype
        self.value = value
        self.mimetype = mimetype
        self.sep = sep
    #}}}

    #{{{def get_info(self):
    def get_info(self):
        output_info = {}
        output_info['type'] = self.type        

        if self.type == 'file':
            output_info['mimetype'] = self.mimetype

        return output_info
    #}}}

    #{{{def __str__(self):
    def __str__(self):
        return ' '.join([ 'type:' + self.type,
                          'value:' + str(self.value),
                          'mimetype:' + str(self.mimetype),
                          'sep:' + str(self.sep)])
    #}}}

    #{{{def copy(self):
    def copy(self):
        return Output(self.type, self.value, self.mimetype, self.sep)
    #}}}

#}}}

#{{{class Service:
class Service:
    logger.info("Inside service class of cm2web from my CGI script.")
    sys.stderr.write("Inside service class of cm2web from my CGI script.\n\n\n")
    #{{{def replace_variable(field, variable_table):
    @staticmethod
    def replace_variable(field, variable_table):
        if field == None:
            return None

        for v in re.findall(r'\$\w+', field):
            if v not in variable_table:
                variable_table[v] = \
                        str(random.randint(0,sys.maxint))
            field = field.replace(v, variable_table[v])
        return field
    #}}}

    #{{{uef load(config):
    @staticmethod
    def load(config):
        required = ['name', 'command', 'arguments', 'output']
        test_required('service', required, config)
        group = config.get('group',"None")

        name = config['name']
        command = config['command']

        arguments = []
        for argument_config in config['arguments']:
            argument = Argument.load(argument_config)
            arguments.append(argument)

        output = Output.load(config['output'])
        if(group != "None"):
            return Service(name, command, arguments, output,group)
        else:
            return Service(name, command, arguments, output)
    #}}}

    #{{{ def __init__(self, name, command, arguments, output):
    def __init__(self, name, command, arguments, output, group='None'):
        self.name = name
        if(group!='None'):
            self.group =group
        self.command = command
        self.arguments = arguments
        self.output = output
        self.variable_table = {}
    #}}}

    #{{{def get_info(self):
    def get_info(self):
        service_info = {}
        service_info['name'] = self.name
        service_info['output'] = self.output.get_info()
        service_info['inputs'] = []
        for argument in self.arguments:
            argument_info = argument.get_info()
            if argument_info != None:
                service_info['inputs'].append(argument_info)

        return service_info
    #}}}

    #{{{def make_cmd(self, args):
    def make_cmd(self, args):
        # //pair flags with  parameter in optional case. Replace_variable..Field might be array
        for arg in self.arguments:
            if arg.fixed:
                self.variable_table['$' + arg.name] = arg.value
            else:
                input_val = args.get(arg.name)
                if arg.type_test(input_val):
                    self.variable_table['$' + arg.name] = input_val
                else:
                    raise Exception('Type mismatch for argument ' + \
                                    arg.name + \
                                    '. Expected ' + \
                                    arg.type) 
        #DO not call replace variable on something that is optional and not provided.
        for i in range(len(self.command)):
            self.command[i] = Service.replace_variable(self.command[i],
                                                       self.variable_table)
        return self.command
    #}}}

    #{{{ def args_match(self, args):
    def args_match(self, args):

        variable_args = []
        for argument in self.arguments:
            if not argument.fixed:
                variable_args.append(argument.name)

        extra = False
        for arg in args:
            if arg == 'service' or arg == 'token':
                continue
            if arg not in variable_args:
                extra = True
                break

        if extra:
            return False

        all_there = True
        for arg in variable_args:
            if arg not in args:
                all_there = False

        if not all_there:
            return False

        return True
    #}}}

    #{{{ def process_result(self, out_file_name):
    def process_result(self, out_file_name):
        sys.stderr.write("\n\n\nInside process result {0}\n\n\n".format(out_file_name))
        if self.output.type == 'text_stream':
            result = {"success":  1}
            out = []
            for line in open(out_file_name, 'r'):
                out.append(line.rstrip().split(self.output.sep))
            result['result'] = out
            return json.dumps(result)
        elif self.output.type == 'file':
            self.output.value = Service.replace_variable(self.output.value,
                                                         self.variable_table)
            return send_file(self.output.value,
                             self.output.mimetype)
    #}}}

    #{{{def copy(self):
    def copy(self):
        name = self.name
        command = self.command[:]
        arguments = []

        for argument in self.arguments:
            arguments.append( argument.copy() )

        output = self.output.copy()
        group="None"
        if(hasattr(self, 'group')):
            group = self.group

        return Service(name, command, arguments, output,group)
    #}}}

#}}}

#{{{class Server:
class Server:
    #{{{def error(msg):
    @staticmethod
    def error(msg):
        err = { 'exception' : msg, "success": 0}
        return json.dumps(err)
    #}}}

    #{{{def load(config_file):
    @staticmethod
    def load(config_file):
        sys.stderr.write("hello there from inside load method ..{0}..\n\n\n ".format(config_file))
        # try:
        #     f = open(config_file, 'r')
        # except ExceInside service class of cm2web from my CGI script.ption as e:
        #      sys.exit('ERROR loading config file. "' + str(e) + '"')
           
        try:
            print("Trying to open file",config_file);
            server_config = settings.Settings(type= "Services",filepath = config_file)
            # server_config = json.load(f)
        except Exception as e:
             sys.exit('ERROR loading server config "' + str(e) + '"')

        # f.close()

        services = {}
        for service_config in server_config:
            service = Service.load(service_config)
            services[service.name] = service

        return Server(services)
    #}}}

    #{{{def __init__(self, services):
    def __init__(self, services):
        self.services = services
    #}}}

    #{{{def get_info(self):
    def get_info(self):
        server_info = {}
        for service in self.services:
            server_info[service] = self.services[service].get_info()
        return server_info
    #}}}

    #{{{def has_service(self, service):
    def has_service(self, service):
        return service in self.services
    #}}}
#}}}

#{{{ class Client:
class Client:
    #{{{class Service:
    class Service:
        #{{{ def load(config):
        @staticmethod
        def load(config):
            name = config['name']
            output = config['output']['type']
            inputs = {}
            for i in config['inputs']:
                inputs[i['name']] = i['type']

            return Client.Service(name, inputs, output)
        #}}}

        #{{{def __init__(self, name, inputs, output):
        def __init__(self, name, inputs, output):
            self.name = name
            self.inputs = inputs
            self.output = output
        #}}}
    #}}}

    #{{{ def connect(url):
    @staticmethod
    def connect(url):
        c = Client(url)
        return c
    #}}}

    #{{{ def __init__(self, url):
    def __init__(self, url):
        self.server_url = url

        self.service_def = None
        try:
            r = requests.get(url + '/info')
            self.service_def = json.loads(r.text)
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError

        self.services = {}

        for service in self.service_def:
            s = Client.Service.load(self.service_def[service])
            self.services[s.name] = s
    #}}}

    #{{{def run(self, service, **kwargs):
    def run(self, service, **kwargs):
        if service not in self.service_def:
            raise Exception('Service "' + service + '" not supported.')

        for i in self.services[service].inputs:
            if i not in kwargs:
                raise Exception('Missing argument "' + i + '".')

        payload = {'service' : service}
        for kwarg in kwargs:
            if kwarg not in self.services[service].inputs:
                raise Exception('Invalid argument "' + kwarg + '".')

            if not Argument.type_check(kwargs[kwarg],
                                       self.services[service].inputs[kwarg]):
                raise Exception('Invalid type for ' + \
                                kwarg + '. Expected ' + \
                                self.services[service].inputs[kwarg])
            payload[kwarg] = kwargs[kwarg]

        r = requests.get(self.server_url, params=payload)

        j = json.loads(r.text)

        if j['success'] != 1:
            message = 'Error.'
            if 'message' in j:
                message += " " + j['message']
            if 'exception' in j:
                message += " " + j['exception']
            raise Exception(message)
        return j['result']
    #}}}
#}}}
