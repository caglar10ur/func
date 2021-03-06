#!/usr/bin/python
# report on any drives with SMART issues
# these are likely going to kick the bucket
# (C) Michael DeHaan, 2007 <mdehaan@redhat.com>
# ===============================================

import func.overlord.client as fc
import func.utils as utils

info = fc.Overlord("*").smart.info()
failures = 0

for (host,details) in info.iteritems():

    if utils.is_error(details):
        print "%s had an error : %s" % (host,details[1:3])
        break

    (rc, list_of_output) = details
    if rc != 0:
        print "============================================"
        print "Host %s may have problems" % host
        print "\n".join(list_of_output[3:])
        failures = failures + 1

print "\n%s systems reported problems" % failures
