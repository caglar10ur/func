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
            vsys_conf = vsys_acl = None 

            l = self.__readFromFile__("/etc/vsys.conf")
            vsys_conf = "/vservers/%(name)s/vsys %(name)s\n" % {"name": slice}
            if not l.__contains__(vsys_conf):
                logger.log("vsys: Adding %s slice to /etc/vsys.conf" % slice)
                l.append([vsys_conf])
                self.__writeToFile__("/etc/vsys.conf",  l)

            try:
                os.mkdir("/vservers/%s/vsys" % slice)
            except OSError:
                pass

            l = self.__readFromFile__("/vsys/%s.acl" % value)
            vsys_acl = "%s\n" % slice  
            if not l.__contains__(vsys_acl)
                logger.log("vsys: Adding %s slice to  /vsys/%s.acl file" % (slice, value))
                l.append([vsys_acl])
                self.__writeToFile__("/vsys/%s.acl" % value, l)

            if vsys_conf != None or vsys_acl != None:
                logger.log("vsys: Restarting vsys service")
                logger.log_call("/etc/init.d/vsys", "restart")

    def DeleteSliceTag(self, slice, tag, value):
         # Sanity check
        try:
            vserver_instance = vserver.VServer(slice)
        except vserver.NoSuchVServer:
            return False

        if tag == "vsys":
            vsys_conf = vsys_acl = None 

            l = self.__readFromFile__("/etc/vsys.conf")
            vsys_conf = "/vservers/%(name)s/vsys %(name)s\n" % {"name": slice}
            if l.__contains__(vsys_conf):
                logger.log("vsys: Adding %s slice to /etc/vsys.conf" % slice)
                l.remove([vsys_conf])
                self.__writeToFile__("/etc/vsys.conf",  l)

            try:
                os.mkdir("/vservers/%s/vsys" % slice)
            except OSError:
                pass

            l = self.__readFromFile__("/vsys/%s.acl" % value)
            vsys_acl = "%s\n" % slice  
            if l.__contains__(vsys_acl)
                logger.log("vsys: Adding %s slice to  /vsys/%s.acl file" % (slice, value))
                l.remove([vsys_acl])
                self.__writeToFile__("/vsys/%s.acl" % value, l)

            if vsys_conf != None or vsys_acl != None:
                logger.log("vsys: Restarting vsys service")
                logger.log_call("/etc/init.d/vsys", "restart")
