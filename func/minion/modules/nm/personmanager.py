# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import sys
import pwd, grp

sys.path.append("/usr/share/NodeManager/")
import logger

class PersonManager():

    version = "0.0.1"
    api_version = "0.0.1"
    description = "PersonManager"

    def AddPersonToSlice(self, slice, persons):
        # get the unix account info
        gid = grp.getgrnam("slices")[2]
        pw_info = pwd.getpwnam(slice)
        uid = pw_info[2]
        pw_dir = pw_info[5]

        # write out authorized_keys file and conditionally create
        # the .ssh subdir if need be.
        dot_ssh = os.path.join(pw_dir,".ssh")
        if not os.path.isdir(dot_ssh):
            if not os.path.isdir(pw_dir):
                logger.verbose("accounts: WARNING: homedir %s does not exist for %s!" % (pw_dir,slice))
                os.mkdir(pw_dir)
                os.chown(pw_dir, uid, gid)
            os.mkdir(dot_ssh)

        auth_keys = os.path.join(dot_ssh, "authorized_keys")
        f = open(auth_keys, "w")
        for i in persons:
            f.write("%s\n" % i["key"])
        f.close()

        # set access permissions and ownership properly
        os.chmod(dot_ssh, 0700)
        os.chown(dot_ssh, uid, gid)
        os.chmod(auth_keys, 0600)
        os.chown(auth_keys, uid, gid)

        logger.log("accounts: %s: installed ssh keys" % slice)

