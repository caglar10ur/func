# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from func.minion.modules import func_module

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

class SliceTagManager(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "SliceTagManager"

    def AddSliceTag(self, slice, tag, value):
        pass
    
    def DeleteSliceTag(self, slice, tag, value):
        pass
