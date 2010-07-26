# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import sys

sys.path.append("/usr/share/NodeManager/")

import vserver
import bwlimit

import logger
import tools

import personmanager
import slicetagmanager

class VServerManager():

    def __startSlice__(self, slice):
        logger.log("slicemanager: %s: starting" % slice)
        q = vserver.VServer(slice)
        q.start()
        logger.log("slicemanager: %s: started" % slice)
        return True

    def __stopSlice__(self, slice):
        logger.log("slicemanager: %s: stoping" % slice)
        q = vserver.VServer(slice)
        q.stop()
        logger.log("slicemanager: %s: stoped" % slice)
        return True

    def __createSlice__(self, slice):
        # Sanity check
        try:
            vserver_instance = vserver.VServer(slice)
        except vserver.NoSuchVServer:
            pass
        else:
            logger.log("slicemanager: %s: Slice already exists" % slice)
            return False

        # FIXME: band-aid for MyPLC 4.x as it has no GetSliceFamily API call
        vref = "planetlab-f8-i386"

        # check the template exists -- there's probably a better way..
        if not os.path.isdir("/vservers/.vref/%s" % vref):
            logger.log ("slicemanager: %s: ERROR Could not create sliver - vreference image %s not found" % (slice, vref))
            return False

        # guess arch
        try:
            (x,y,arch) = vref.split("-")
            # mh, this of course applies when "vref" is e.g. "netflow"
            # and that"s not quite right
        except:
            arch="i386"

        def personality (arch):
            personality = "linux32"
            if arch.find("64") >= 0:
                personality = "linux64"
            return personality

        logger.log("slicemanager: %s: creating" % slice)
        logger.log_call("/bin/bash","-x","/usr/sbin/vuseradd", "-t", vref, slice)
        logger.log("slicemanager: %s: created" % slice)

        # export slicename to the slice in /etc/slicename
        file("/vservers/%s/etc/slicename" % slice, "w").write(slice)
        file("/vservers/%s/etc/slicefamily" % slice, "w").write(vref)

        # set personality: only if needed (if arch"s differ)
        if tools.root_context_arch() != arch:
            file("/etc/vservers/%s/personality" % slice, "w").write(personality(arch)+"\n")
            logger.log("slicemanager: %s: set personality to %s" % (slice, personality(arch)))

        return True


    def AddSliceToNode(self, slice, tags, keys):
        if self.__createSlice__(slice) == True:
            p = personmanager.PersonManager()
            p.AddPersonToSlice(slice, keys)

            s = slicetagmanager.SliceTagManager()
            for tag in tags:
                s.AddSliceTag(slice, tag)

            bwlimit.set(bwlimit.get_xid(slice))

            self.__startSlice__(slice)
        else:
            return False
        return True

    def DeleteSliceFromNode(self, slice):
        logger.log_call("/bin/bash", "-x", "/usr/sbin/vuserdel", slice)
        return True
