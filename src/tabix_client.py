import sys
from cyvcf2 import VCF
import argparse
import cmd2web

parser = argparse.ArgumentParser(description='Annotate VCF with STIX ws.')

parser.add_argument('--port',
		    dest='port',
		    default="8080",
		    help='Port server is running on(default 8080)')

parser.add_argument('--host',
		    dest='host',
                    default="127.0.0.1",
                    help='Server address(default http://127.0.0.1)')

parser.add_argument('--chromosome',
		    dest='chromosome',
		    required=True)

parser.add_argument('--start',
		    dest='start',
		    required=True)

parser.add_argument('--end',
		    dest='end',
		    required=True)

parser.add_argument('--service',
		    dest='service',
		    required=True)


args = parser.parse_args()

s = cmd2web.Client.connect(args.host, args.port)

try:
    R = s.run(args.service,
              chromosome=args.chromosome,
              start=args.start,
              end=args.end)
except Exception as e:
    print(str(e))

for r in R:
    print('\t'.join(r))
