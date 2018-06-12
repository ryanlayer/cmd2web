import cmd2web

s = cmd2web.Client.connect('127.0.0.1','8080')

try:
    s.run('chainSelf', chromosome='chr1', start='z10000', end =50000)
except Exception, e:
    print str(e)

try:
    s.run('chainSelf', chromosome='chr1', end =50000)
except Exception, e:
    print str(e)

R = s.run('chainSelf', chromosome='chr1', start=10000, end =50000)

for r in R:
    print '\t'.join(r)
