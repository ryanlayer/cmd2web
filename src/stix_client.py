import sys
from cyvcf2 import VCF
import argparse
import cmd2web

parser = argparse.ArgumentParser(description='Annotate VCF with STIX ws.')

parser.add_argument('--port',
		    dest='port',
		    type=int,
		    default="8080",
		    help='Port server is running on(default 8080)')

parser.add_argument('--host',
		    dest='host',
		    default="127.0.0.1",
		    help='Server address(default 127.0.0.1)')

parser.add_argument('--vcf',
		    dest='vcf_file_name',
		    required=True,
		    help='Name of VCF to annotate')

args = parser.parse_args()

vcf = VCF(args.vcf_file_name)
s = cmd2web.Client.connect('127.0.0.1','8080')

for v in vcf:
    chrom =  v.CHROM
    start = v.POS
    end = v.INFO.get('END')
    svtype = v.INFO.get('SVTYPE')
    cipos = v.INFO.get('CIPOS')
    ciend = v.INFO.get('CIEND')

    if None in [chrom, start, end, svtype, cipos, ciend]:
        continue

    if svtype not in ['DEL', 'DUP', 'INV']:
        continue

    #print [chrom, start, end, svtype, cipos, ciend]
    try:
        R = s.run('1kg', 
                  type=svtype,
                  left_chrom=chrom, left_start=start+cipos[0], left_end=start+cipos[1],
                  right_chrom=chrom, right_start=end+ciend[0], right_end=end+ciend[1])
    except Exception as e:
        print(str(e))
        continue

    print(R)

