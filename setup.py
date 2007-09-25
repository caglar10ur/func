#!/usr/bin/python

import sys
from distutils.core import setup, Extension
#from setuptools import setup,find_packages
import string
import glob

NAME = "func"
VERSION = open("version", "r+").read().split()[0]
SHORT_DESC = "%s remote configuration and management api" % NAME
LONG_DESC = """
A small pluggable xml-rpc daemon used by %s to implement various web services hooks
""" % NAME


if __name__ == "__main__":
 
        manpath    = "share/man/man1/"
        etcpath    = "/etc/%s" % NAME
        etcpathdb  = "/etc/%s/db" % NAME
        wwwpath    = "/var/www/%s" % NAME
        initpath   = "/etc/init.d/"
        logpath    = "/var/log/%s/" % NAME
        logpathdb  = "/var/log/%s/db/" % NAME
	settingspath = "/var/lib/%s/" % NAME
        migraterepopath = "/var/lib/%s/db/" % NAME
	schemapath = "/usr/share/%s/db_schema/" % NAME
	upgradepath = schemapath + "upgrade/"
	puppetpath = "/usr/share/%s/puppet-config/" % NAME
	manifestpath = "/etc/puppet/manifests/"
	profiletemplatepath = "/usr/share/%s/profile-template/" % NAME
        profilespath    = "/var/lib/%s/profiles/" % NAME
        queuedprofilespath    = "/var/lib/%s/profiles/queued/" % NAME
        setup(
                name="%s" % NAME,
                version = VERSION,
                author = "Lots",
                author_email = "func-list@redhat.com",
                url = "https://hosted.fedoraproject.org/projects/func/",
                license = "GPL",
		scripts = ["scripts/funcd", "scripts/certmaster"],
		# package_data = { '' : ['*.*'] },
                package_dir = {"%s" % NAME: "%s" % NAME,
			       "%s/minion" % NAME: "minion/",
			       "%s/minion/modules" % NAME: "modules/",
			       "%s/overlord" % NAME: "overlord/"
                },
		packages = ["%s" % NAME,
	        	    "%s/minion" % NAME,
			    "%s/overlord" % NAME,
	        	    "%s/minion/modules" % NAME
                ],
                data_files = [(initpath, ["init-scripts/funcd", "init-scripts/certmaster"]),
                              (etcpath, ["settings","etc/certmaster.conf"]),
			      (etcpathdb, []),
			      (logpath, []),
			      (logpathdb, []),
			      (migraterepopath, []),
			      (profilespath, []),
			      (queuedprofilespath, [])],
                description = SHORT_DESC,
                long_description = LONG_DESC
        )

