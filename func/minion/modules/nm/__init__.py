# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 
from func.minion.modules import func_module

from slicetagmanager import SliceTagManager
from vservermanager import VServerManager
from personmanager import PersonManager

class NM(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "NodeManager"

    def AddSliceToNode(self, slice, tags, keys):
        VServerManager.AddSliceToNode (self, slice, tags, keys)
   
    def DeleteSliceFromNode(self, slice):
        VServerManager.DeleteSlice(self, slice)

    def AddSliceTag(self, slice, tag, value):
        SliceTagManager.AddSliceTag(self, slice, tag, value)

    def DeleteSliceTag(self, slice, tag, value):
        SliceTagManager.DeleteSliceTag(self, slice, tag, value)

    def AddPersonToSlice(self, slice, persons):
        PersonManager.AddPersonToSlice(self, slice, persons)
