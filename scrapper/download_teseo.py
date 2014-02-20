import os
import sys
import gzip
import glob
import json
import time
import shutil
import urllib2
import datetime
import traceback

FNAME = 'empty.json'
TMP_FNAME = 'empty.tmp.json'

MAX = 1200000

print "Loading %s (in case of error, copy %s into %s)..." % (FNAME, TMP_FNAME, FNAME),
sys.stdout.flush()
if os.path.exists(FNAME):
   empty_phds = json.load(open(FNAME))
else:
   empty_phds = []
print "[done]"
sys.stdout.flush()

empty_phd_contents = urllib2.urlopen("https://www.educacion.gob.es/teseo/mostrarRef.do?ref=1").read()
empty_phd_contents_length = len(empty_phd_contents) + 100

valid_phds = 0
max_number = 0

print "Loading downloaded files files...",
sys.stdout.flush()
for f in glob.glob("data/[0-9]*.html.gz"):
    try:
        number = int(os.path.basename(f).split('.html.gz')[0])
    except:
        continue
    else:
        valid_phds += 1
        max_number = max(max_number, number)
print "[done]"
sys.stdout.flush()

try:
    max_number = max(empty_phds[-1], max_number)
except:
    max_number = 0

while True:
    try:
        for identifier in xrange(max_number, MAX):
           print "%s Loading %s (%.1f%%) - %s valid files" % (datetime.datetime.now().ctime(), identifier, 100.0 * identifier / MAX, valid_phds),
           phd_fname = 'data/%s.html.gz' % identifier
           if identifier not in empty_phds and not os.path.exists(phd_fname):
              url_base = 'https://www.educacion.es/teseo/mostrarRef.do?ref='
              url = url_base + str(identifier)
              phd_contents = urllib2.urlopen(url).read()
              if url_base in phd_contents:
                 bookmark_url = url_base + (phd_contents.split(url_base)[1].split('<a')[0])
              else:
                 bookmark_url = 'not found'
              if len(phd_contents) < empty_phd_contents_length or bookmark_url != url:
                 empty_phds.append(identifier)
                 json.dump(empty_phds, open(TMP_FNAME, 'w'))
                 shutil.copyfile(TMP_FNAME, FNAME)
                 print "[empty]"
              else:
                 gzip.open(phd_fname, 'w').write(phd_contents)
                 print "[downloaded]"
                 valid_phds += 1
           else:
              if os.path.exists(phd_fname):
                 valid_phds += 1
              print "[cached]"
        
           if identifier % 10 == 0:
              sys.stdout.flush()
        break
    except:
        traceback.print_exc()
        print "Waiting 180 seconds"
        sys.stdout.flush()
        sys.stderr.flush()
        time.sleep(180)   
  
