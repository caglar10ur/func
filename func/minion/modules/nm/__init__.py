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

def check_revision(function_name):
    def _wrapper(*args, **kwargs):
        # FIXME: args[X] will be a revision number in future
        # if our-revision != API-revision --> out-of-sync
        if True:
            return function_name(*args, **kwargs)
        else:
            import logger
            logger.log("Out-of-sync!...")
            return False
    return _wrapper


class NM(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "NodeManager"

    @check_revision
    def AddSliceToNode(self, slice, tags, keys):
        nm = VServerManager()
        return nm.AddSliceToNode(slice, tags, keys)

    @check_revision
    def DeleteSliceFromNode(self, slice):
        nm = VServerManager()
        return nm.DeleteSliceFromNode(slice)

    @check_revision
    def AddSliceTag(self, slice, tag, value):
        nm = SliceTagManager()
        return nm.AddSliceTag(slice, tag, value)

    @check_revision
    def DeleteSliceTag(self, slice, tag, value):
        nm = SliceTagManager()
        return nm.DeleteSliceTag(slice, tag, value)

    @check_revision
    def AddPersonToSlice(self, slice, persons):
        nm = PersonManager()
        return nm.AddPersonToSlice(slice, persons)

    @check_revision
    def DeletePersonFromSlice(self, slice, persons):
        nm = PersonManager()
        # Adds all keys to slice
        return nm.AddPersonToSlice(slice, persons)

    def register_method_args(self):
        return {
                "AddSliceToNode":
                {
                    "args":
                    {
                        "slice":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"slice name"
                        },
                        "tags":
                        {
                            "type":"list",
                            "optional":False,
                            "description":"tags"
                        },
                        "keys":
                        {
                            "type":"list",
                            "optional":False,
                            "description":"keys"
                        },
                    },
                    "description": "AddSliceToNode"
                },
                "DeleteSliceFromNode":
                {
                    "args":
                    {
                        "slice":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"slice name"
                        },
                    },
                    "description": "DeleteSliceFromNode"
                },


                "AddSliceTag":
                {
                    "args":
                    {
                        "slice":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"slice name"
                        },
                        "tag":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"tag name"
                        },
                        "value":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"tag value"
                        },
                    },
                    "description": "AddSliceTag"
                },
                "DeleteSliceTag":
                {
                    "args":
                    {
                        "slice":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"slice name"
                        },
                        "tag":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"tag name"
                        },
                        "value":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"tag value"
                        },
                    },
                    "description": "DeletSliceTag"
                },
                "AddPersonToSlice":
                {
                    "args":
                    {
                        "slice":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"slice name"
                        },
                        "persons":
                        {
                            "type":"list",
                            "optional":False,
                            "description":"person keys name"
                        },
                    },
                    "description": "AddPersonToSlice"
                },
                "DeletePersonFromSlice":
                {
                    "args":
                    {
                        "slice":
                        {
                            "type":"string",
                            "optional":False,
                            "description":"slice name"
                        },
                        "persons":
                        {
                            "type":"list",
                            "optional":False,
                            "description":"person keys name"
                        },
                    },
                    "description": "DeletePersonFromSlice"
                },
            }
