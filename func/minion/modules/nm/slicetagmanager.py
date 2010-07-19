# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import fcntl
import os
import pwd, grp
import shutil
import socket
import sys

sys.path.append("/usr/share/NodeManager/")

import logger
import vserver
import bwlimit

class SliceTagManager():

    version = "0.0.1"
    api_version = "0.0.1"
    description = "SliceTagManager"

    def __readFromFile__(self, filename):
        if os.path.exists(filename):
            f = open(filename, "r")
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            filecontent = f.readlines()
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            f.close()
        else:
            filecontent = []

        return filecontent

    def __writeToFile__(self, filename, filecontent, sorted = True):
        f = open(filename,"w")
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

        sortedfilecontent = filecontent
        if sorted == True:
            sortedfilecontent = list(set(filecontent))
            sortedfilecontent.sort()

        for i in sortedfilecontent:
            f.write("%s" % i)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()

    def AddSliceTag(self, slice, tag, value):
        # Sanity check
        try:
            vserver_instance = vserver.VServer(slice)
        except vserver.NoSuchVServer:
            return False

        if tag == "vsys":
            logger.log("vsys: Adding %s slice to /etc/vsys.conf" % slice)

            l = self.__readFromFile__("/etc/vsys.conf")
            vsys_conf = "/vservers/%(name)s/vsys %(name)s\n" % {"name": slice}
            l.append([vsys_conf])
            self.__writeToFile__("/etc/vsys.conf",  l)

            try:
                os.mkdir("/vservers/%s/vsys" % slice)
            except OSError:
                pass

            logger.log("vsys: Adding %s slice to /vsys/%s.acl file" % (slice, value))

            l = self.__readFromFile__("/vsys/%s.acl" % value)
            vsys_acl = "%s\n" % slice  
            l.append([vsys_acl])
            self.__writeToFile__("/vsys/%s.acl" % value, l)

            logger.log("vsys: Restarting vsys service")
            logger.log_call("/etc/init.d/vsys", "restart")

        if tag.startswith("vsys_"):
            VSYS_PRIV_DIR = "/etc/planetlab/vsys-attributes"

            logger.log("vsys_privs: Updating %s/%s/%s" % (VSYS_PRIV_DIR, slice, tag))

            if not os.path.exists("%s/%s" % (VSYS_PRIV_DIR, slice)):
                os.mkdir("%s/%s" % (VSYS_PRIV_DIR, slice))

            l = self.__readFromFile__("%s/%s/%s" % (VSYS_PRIV_DIR, slice, tag))
            l.append(["%s\n" % value])
            self.__writeToFile__("%s/%s/%s" % (VSYS_PRIV_DIR, slice, tag),  l)

            logger.log("vsys_privs: Added vsys attribute %s for %s" % (value, slice))

        if tag == "codemux":
            logger.log("codemux: Updating slice %s using %s" % (slice, value))

            parts = value.split(",")
            if len(parts)<2:
                logger.log("codemux: Attribute value (%s) for codemux not separated by comma. Skipping." % value)
                return False

            if len(parts) == 3:
                ip = parts[2]
            else:
                ip = ""
            params = {'host': parts[0], 'port': parts[1], 'ip': ip}

            l = self.__readFromFile__("/etc/codemux/codemux.conf")
            l.append(["%s %s %s %s\n" % (params["host"], slice, params["port"], params["ip"])])
            self.__writeToFile__("/etc/codemux/codemux.conf",  l)

            logger.log("codemux: Restarting codemux service")
            logger.log_call("/etc/init.d/codemux","condrestart")

    def DeleteSliceTag(self, slice, tag, value):
         # Sanity check
        try:
            vserver_instance = vserver.VServer(slice)
        except vserver.NoSuchVServer:
            return False

        if tag == "vsys":
            logger.log("vsys: Removing %s slice from /etc/vsys.conf" % slice)

            l = self.__readFromFile__("/etc/vsys.conf")
            vsys_conf = "/vservers/%(name)s/vsys %(name)s\n" % {"name": slice}
            if l.__contains__(vsys_conf):
                l.remove([vsys_conf])
            self.__writeToFile__("/etc/vsys.conf",  l)

            try:
                os.mkdir("/vservers/%s/vsys" % slice)
            except OSError:
                pass

            logger.log("vsys: Removing %s slice from /vsys/%s.acl file" % (slice, value))

            l = self.__readFromFile__("/vsys/%s.acl" % value)
            vsys_acl = "%s\n" % slice  
            if l.__contains__(vsys_acl):
                l.remove([vsys_acl])
            self.__writeToFile__("/vsys/%s.acl" % value, l)
            
            logger.log("vsys: Restarting vsys service")
            logger.log_call("/etc/init.d/vsys", "restart")

        if tag.startswith("vsys_"):
            VSYS_PRIV_DIR = "/etc/planetlab/vsys-attributes"

            logger.log("vsys_privs: Removing %s/%s/%s" % (VSYS_PRIV_DIR, slice, tag))

            l = self.__readFromFile__("%s/%s/%s" % (VSYS_PRIV_DIR, slice, tag))
            l.append(["%s\n" % value])
            if l.__contains__("%s\n" % value):
                l.remove("%s\n" % value)

            if l == []:
                shutil.rmtree("%s/%s" % (VSYS_PRIV_DIR, slice))
            else:
                self.__writeToFile__("%s/%s/%s" % (VSYS_PRIV_DIR, slice, tag),  l)

            logger.log("vsys_privs: Removed vsys attribute %s for %s" % (value, slice))

        if tag == "codemux":
            logger.log("codemux: Updating slice %s using %s" % (slice, value))

            parts = value.split(",")
            if len(parts)<2:
                logger.log("codemux: Attribute value (%s) for codemux not separated by comma. Skipping." % value)
                return False

            if len(parts) == 3:
                ip = parts[2]
            else:
                ip = ""
            params = {'host': parts[0], 'port': parts[1], 'ip': ip}

            l = self.__readFromFile__("/etc/codemux/codemux.conf")
            if l.__contains__("%s %s %s %s\n" % (params["host"], slice, params["port"], params["ip"])):
                l.remove("%s %s %s %s\n" % (params["host"], slice, params["port"], params["ip"]))
            self.__writeToFile__("/etc/codemux/codemux.conf",  l)

            logger.log("vsys: Restarting codemux service")
            logger.log_call("/etc/init.d/codemux","condrestart")
