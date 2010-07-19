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

    def AddSliceToNode(self, slice, tags, keys):
        pass

    def DeleteSliceFromNode(self, slice):
        logger.log_call("/bin/bash", "-x", "/usr/sbin/vuserdel", slice)
        return True


