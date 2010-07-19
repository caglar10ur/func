# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from func.minion.modules import func_module

import os
import sys

sys.path.append("/usr/share/NodeManager/")

import vserver
import bwlimit

import logger
import tools

import personmanager
import slicetagmanager

class VServerManager(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "VServer"

    def AddSliceToNode(self, slice, tags, keys):
        pass

    def DeleteSliceFromNode(self, slice):
        pass
