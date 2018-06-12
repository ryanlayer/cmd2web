`cmd2web` is a simple framework for enabling a RESTful web interface to command
line programs. From this interface, data and methods can be easily accessed
through either a dynamic website or a programmatic interface. This package
includes a server and client javascript and python interfaces.

# Server

To stand up a server, you define a mapping between command line parameters and
URL query parameters in a JSON config file. Each command line instance is
referred to as a service, and a server can host multiple services.

In this example, we will consider a server with just one service to the `tabix`
program (https://github.com/samtools/htslib) and the Repeat Masker track from
UCSC genome browser (based on
http://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/rmsk.txt.gz).k

From the `tabix` manual:
```
Tabix indexes a TAB-delimited genome position file in.tab.bgz and creates an
index file ( in.tab.bgz.tbi or in.tab.bgz.csi ) when region is absent from the
command-line. The input data file must be position sorted and compressed by
bgzip which has a gzip(1) like interface.

After indexing, tabix is able to quickly retrieve data lines overlapping
regions specified in the format "chr:beginPos-endPos". (Coordinates specified
in this region format are 1-based and inclusive.)
```

To use `tabix` on the command line, you pass the file name and the region of
interest and all intervals in the file that overlap that region are returned.
```
$ tabix rmsk.bed.gz chr1:10000-20000
chr1    10000   10468   (CCCTAA)n   Simple_repeat   Simple_repeat
chr1    10468   11447   TAR1    Satellite   telo
chr1    11503   11675   L1MC    LINE    L1
chr1    11677   11780   MER5B   DNA hAT-Charlie
chr1    15264   15355   MIR3    SINE    MIR
chr1    16712   16749   (TGG)n  Simple_repeat   Simple_repeat
chr1    18906   19048   L2a LINE    L2
chr1    19947   20405   L3  LINE    CR1
```

The URL for this service looks very similar to the command line invocation:
```
$ curl "http://127.0.0.1:8080/?service=rmsk&chromosome=chr1&start=10000&end=20000"
{ "success": 1,
  "result": [
    [ "chr1", "10000", "10468", "(CCCTAA)n", "Simple_repeat", "Simple_repeat" ],
    [ "chr1", "10468", "11447", "TAR1", "Satellite", "telo" ],
    [ "chr1", "11503", "11675", "L1MC", "LINE", "L1" ],
    [ "chr1", "11677", "11780", "MER5B", "DNA", "hAT-Charlie" ],
    [ "chr1", "15264", "15355", "MIR3", "SINE", "MIR" ],
    [ "chr1", "16712", "16749", "(TGG)n", "Simple_repeat", "Simple_repeat" ],
    [ "chr1", "18906", "19048", "L2a", "LINE", "L2" ],
    [ "chr1", "19947", "20405", "L3", "LINE", "CR1" ]
  ]
}
```
 
## Server config

A skeleton of the config is:

```
[
    {
        "name" : "",
        "arguments" :
        [
            {
                "name" : "",
                "fixed" : "",
                "type" : "",
                "value" : ""
            },
        ],
        "command": [ "" ],

        "output" :
        {
            "type" : ""
            "sep" : ""
        }
    }
]
```

Each element in the config is described below.

### name
Since a server can host many services, the first step is to define the service
name. Requests will use the `service` URL query attribute to the name of the
service. The server will return an exception for any requests that do not have
service specified:
```
$ curl "http://127.0.0.1:8080/?chromosome=chr1&start=10000&end=20000"
{"exception": "No service specified", "success": 0}
```

Here the name is `rmsk`:
```
"name" : "rmsk"
```

### arguments

This command has five arguments:
1. path to the executable (`tabix`)
2. file of interest (`rmsk.bed.gz`)
3. chromosome (`chr1`)
4. start (`10000`)
5. end (`20000`)

Each of these attributes is specified in a `arguments` array.  Attributes can
be fixed (`"fixed" : "true"`) or variable ("fixed" : "false)".  The value of
the variable attributes will be defined in a users' query, and the fixed
attributes are defined by the `value` field. Each attribute has a type that is
checked by the server before executing any commands. Currently `string`,
`integer`, and `float` are supported.

The arguments array for this service is:
```
"arguments" :
[
    {
        "name" : "file",
        "fixed" : "true",
        "type" : "string",
        "value" : "/data/rmsk.bed.gz"
    },
    {
        "name" : "chromosome",
        "fixed" : "false",
        "type" : "string"
    },
    {
        "name" : "start",
        "fixed" : "false",
        "type" : "integer"
    },
    {
        "name" : "end",
        "fixed" : "false",
        "type" : "integer"
    }
]
```

When a user requests this service, the server fills a variable table with both
fixed and variable attributes. The server will return an exception for requests
that do not provide precisely the set of variable arguments.
```
$ curl "http://127.0.0.1:8080/?service=rmsk&chromosome=chr1&start=10000"
{"exception": "Argument mismatch", "success": 0}
```
The server will also return an exception for requests with type mismatches.
```
$ curl "http://127.0.0.1:8080/?service=rmsk&chromosome=chr1&start=10000&end=not_int"
{"exception": "Type mismatch for argument end. Expected integer", "success": 0}
```

### command
After the variable table is filled, the server will construct the command by
replaced variables names with value in the variable table by the same name.
Note that variables in the command start with '$', but the names of the
attributes do not.  To improve security, it is highly recommended to split the
command into individual strings.
```
"command":
[
    "/usr/bin/tabix",
    "$file",
    "$chromosome:$start-$end"
],
```

The constructed command is then executed locally on the server.  While it is
beyond the scope of this example, we highly recommend running commands through
a virtual machine such as docker.

The server will return an exception for any command that does not return with a
zero exit code. Commands also have a maximum runtime that is specified by the
`--timeout` option when starting the server. The server will return an
exception if a command exceeds this limit.

### output

The last step is to define the output type. Current `text_stream` and `file`
are supported.
```
"output" :
{
    "type" : "text_stream",
    "sep" : "\t"
}
```

For `text_stream` output, the server returns a JSON array or arrays. Output is split
by line then by the value given in the `sep` field.

## staring the server

```
python server.py --config tabix_config.json
```

```
usage: server.py [-h] --config CONFIG [--port PORT] [--host HOST]
                 [--timeout TIMEOUT]

command to web server.

optional arguments:
  -h, --help         show this help message and exit
  --config CONFIG    Configuration file.
  --port PORT        Port to run on (default 8080)
  --host HOST        Server hos (default 127.0.0.1)
  --timeout TIMEOUT  Max runtime (sec) for a command (default 10)
```

In addition to serving requests, the server also advertises the services it
supports along with input and output requirements. This information allows for
the development of more general clients interfaces and can be accessed at the
`\info` endpoint.

```
$ curl "http://127.0.0.1:8080/info"
{
    "rmsk": {
	"name": "rmsk",
	"output": { "type": "text_stream" },
        "inputs": [ 
          { "name": "chromosome", "type": "string" },
	  { "name": "start", "type": "integer" },
	  { "name": "end", "type": "integer" }
	]
      }
}
```

# Client

Any method that can make web request can be a client. For example, `curl` works
great.
```
$ curl "http://127.0.0.1:8080/?service=rmsk&chromosome=chr1&start=10000&end=20000"
{ "success": 1,
  "result": [
    [ "chr1", "10000", "10468", "(CCCTAA)n", "Simple_repeat", "Simple_repeat" ],
    [ "chr1", "10468", "11447", "TAR1", "Satellite", "telo" ],
    [ "chr1", "11503", "11675", "L1MC", "LINE", "L1" ],
    [ "chr1", "11677", "11780", "MER5B", "DNA", "hAT-Charlie" ],
    [ "chr1", "15264", "15355", "MIR3", "SINE", "MIR" ],
    [ "chr1", "16712", "16749", "(TGG)n", "Simple_repeat", "Simple_repeat" ],
    [ "chr1", "18906", "19048", "L2a", "LINE", "L2" ],
    [ "chr1", "19947", "20405", "L3", "LINE", "CR1" ]
  ]
}
```

This package also provides a python API that is tightly coupled with the
server.  For example, exceptions returned by the server are then raised as an
exception by the API. The client will also perform local type checking on all
service requests before submitting them to the server.

The client has two steps
1. connecting to the server with `cmd2web.Client.connect(host, port)`
2. running a query with `run(service_name, **kwargs)` where the `kwargs` map to
   the services variable arguments

To use the service defined above:
```
import cmd2web
s = cmd2web.Client.connect('127.0.0.1','8080')
R =  R = s.run('rmsk', chromosome="chr1", start=10000, end=20000)
for r in R:
    print('\t'.join(r))
``` 

# Installation

The easiest way to install `cmd2web` is with `virtualenv`:
```
virtualenv -p /usr/local/bin/python3.6 cmd2web_env
source cmd2web_env/bin/activate
cd cmd2web/
pip install flask requests numpy Cython cyvcf2
source cmd2web_env/bin/activate
```
