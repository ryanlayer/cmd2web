import sys
from cyvcf2 import VCF
import argparse
import cmd2web

parser = argparse.ArgumentParser(description='Annotate VCF with STIX ws.')

parser.add_argument('--host',
		    dest='host',
                    default="http://127.0.0.1:8080",
                    help='Server address(default http://127.0.0.1:8080)')

parser.add_argument('--vcf',
		    dest='vcf_file_name',
		    required=True,
		    help='Name of VCF to annotate')

args = parser.parse_args()

vcf = VCF(args.vcf_file_name)

s = cmd2web.Client.connect(args.host)

vcf.add_info_to_header({'ID': 'STIX_NONZERO',
                        'Description': 'The number of samples in cohort with non-zero evidence',
                        'Type':'Integer', 'Number': '1'})

print (str(vcf.raw_header), end='', flush=True)

for v in vcf:
    chrom =  v.CHROM
    start = v.POS
    end = v.INFO.get('END')
    svtype = v.INFO.get('SVTYPE')
    cipos = v.INFO.get('CIPOS')
    ciend = v.INFO.get('CIEND')

    if None in [chrom, start, end, svtype]:
        continue

    if cipos == None:
        cipos = [0,0]

    if ciend == None:
        ciend = [0,0]

    if svtype not in ['DEL', 'DUP', 'INV']:
        continue

    #print [chrom, start, end, svtype, cipos, ciend]
    try:
        R = s.run('1kg', 
                  type=svtype,
                  left_chrom=chrom, left_start=start+cipos[0], left_end=start+cipos[1],
                  right_chrom=chrom, right_start=end+ciend[0], right_end=end+ciend[1])
    except Exception as e:
        print(str(v), end='', flush=True)
        continue

    zero_one = [int(x) for x in R[0][2].split(':')]
    more_depths = [int(x) for x in R[0][4].split(':')]
    non_zero_depths = zero_one[1] + sum(more_depths)
    v.INFO["STIX_NONZERO"] = str(non_zero_depths)
    print(str(v), end='', flush=True)
