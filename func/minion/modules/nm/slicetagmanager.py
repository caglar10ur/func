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
            l += [vsys_conf]
            self.__writeToFile__("/etc/vsys.conf",  l)

            try:
                os.mkdir("/vservers/%s/vsys" % slice)
            except OSError:
                pass

            logger.log("vsys: Adding %s slice to /vsys/%s.acl file" % (slice, value))

            l = self.__readFromFile__("/vsys/%s.acl" % value)
            vsys_acl = "%s\n" % slice  
            l += [vsys_acl]
            self.__writeToFile__("/vsys/%s.acl" % value, l)

            logger.log("vsys: Restarting vsys service")
            logger.log_call("/etc/init.d/vsys", "restart")

        if tag.startswith("vsys_"):
            VSYS_PRIV_DIR = "/etc/planetlab/vsys-attributes"

            logger.log("vsys_privs: Updating %s/%s/%s" % (VSYS_PRIV_DIR, slice, tag))

            if not os.path.exists("%s/%s" % (VSYS_PRIV_DIR, slice)):
                os.mkdir("%s/%s" % (VSYS_PRIV_DIR, slice))

            l = self.__readFromFile__("%s/%s/%s" % (VSYS_PRIV_DIR, slice, tag))
            l += ["%s\n" % value]
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
            l += ["%s %s %s %s\n" % (params["host"], slice, params["port"], params["ip"])]
            self.__writeToFile__("/etc/codemux/codemux.conf",  l)

            logger.log("codemux: Restarting codemux service")
            logger.log_call("/etc/init.d/codemux","condrestart")

        if tag == "cpu_share":
            logger.log("cpu_share: Updating %s slice with cpu_share value %s" % (slice, value))

            vserver_instance.set_sched_config(0, value)

        if tag == "disk_max":
            logger.log("disk_max: Updating %s slice with disk_max value %s" % (slice, value))

            logger.log("disk_max: %s: computing disk usage: beginning" % slice)
            vserver_instance.init_disk_info()
            logger.log("disk_max: %s: computing disk usage: ended" % slice)

            logger.log("disk_max: %s: setting max disk usage to %s KiB" % (slice, value))
            vserver_instance.set_disklimit(max(int(value), vserver_instance.disk_blocks))

        if tag == "capabilities":
            logger.log("capabilities: Updating %s slice with capabilities value %s" % (slice, value))

            vserver_instance.set_capabilities_config(value)

        if tag == "ip_addresses":
            logger.log("ip_addresses: Updating %s slice with ip_addresses value %s" % (slice, value))

            for ip in value.split(","):
                 if len(ip.split(".")) == 4:
                     try:
                         socket.inet_aton(ip)
                     except socket.error:
                         logger.log("ip_addresses: Attribute value (%s) for ip_addresses is not a valid IP. Skipping." % ip)
                         return False
                 else:
                     logger.log("codemux: Attribute value (%s) for ip_addresses not separated by dot. Skipping." % ip)
                     return False

            vserver_instance.set_ipaddresses_config(value)

#        if tag == "initscript":
#            logger.log("initscript: Updating %s slice with initscript value %s" % (slice, value[0]["name"]))
#
#            vinit = open("/usr/share/NodeManager/sliver-initscripts/vinit").readlines()
#            self.__writeToFile__("/vservers/%s/etc/rc.d/init.d/vinit" % slice, vinit, False)
#            os.chmod("/vservers/%s/etc/rc.d/init.d/vinit" % slice, 0755)
#            try:
#                os.symlink("../init.d/vinit", "/vservers/%s/etc/rc.d/rc3.d/S99vinit" % slice)
#            except OSError:
#                pass

#            self.__writeToFile__("/vservers/%s/etc/rc.d/init.d/vinit.slice" % slice ,value[0]["script"], False)
#            os.chmod("/vservers/%s/etc/rc.d/init.d/vinit.slice" % slice, 0755)

#            if value[0]["enabled"] == True:
#                logger.log("initscript: Starting %s slice with initscript value %s" % (slice, value[0]["name"]))

        if tag == "enabled":
            logger.log("enabled: Updating %s slice with enabled value %s" % (slice, value))

            if int(value) > 0:
                 # FIXME: SLICE ID
                 vserver_instance.start()
            else:
                logger.log("enabled: disabling remote login for %s" % slice)
                # FIXME: suspend is not supported with cgroups!
                vserver_instance.stop()

        if tag.endswith("_min") or tag.endswith("_soft") or tag.endswith("_hard"):
            logger.log("rlimit: Updating %s slice with rlimit %s with value %s" % (slice, tag, value))

            # special constant that tells vserver to keep its existing settings
            KEEP_LIMIT = vserver.VC_LIM_KEEP

            # populate the sliver/vserver specific default allocations table,
            # which is used to look for slice attributes
            DEFAULT_ALLOCATION = {}

            rlimit = tag.split("_")[0]
            DEFAULT_ALLOCATION["%s_min" % rlimit] = KEEP_LIMIT
            DEFAULT_ALLOCATION["%s_soft" % rlimit] = KEEP_LIMIT
            DEFAULT_ALLOCATION["%s_hard" % rlimit] = KEEP_LIMIT

            DEFAULT_ALLOCATION["%s" % tag] = int(value)

            update = vserver_instance.set_rlimit(rlimit.upper(),
                            DEFAULT_ALLOCATION["%s_hard" % rlimit],
                            DEFAULT_ALLOCATION["%s_soft" % rlimit],
                            DEFAULT_ALLOCATION["%s_min" % rlimit])

            if update:
                logger.log("rlimit: setting rlimit %s to (%s, %s, %s)" %
                            (rlimit.upper(),
                            DEFAULT_ALLOCATION["%s_hard" % rlimit],
                            DEFAULT_ALLOCATION["%s_soft" % rlimit],
                            DEFAULT_ALLOCATION["%s_min" % rlimit]))

        if tag.startswith("net_"):
            logger.log("bwlimit: Adding bwlimit %s to %s slice with %s value" % (tag, slice, value))

            DEFAULT_ALLOCATION = {}

            slice_xid = bwlimit.get_xid(slice)
            current_state = bwlimit.get(slice_xid)

            if current_state is not None:
                DEFAULT_ALLOCATION["net_share"] = int(current_state[1])
                DEFAULT_ALLOCATION["net_min_rate"] = int(current_state[2] / 1000)
                DEFAULT_ALLOCATION["net_max_rate"] = int(current_state[3] / 1000)
                DEFAULT_ALLOCATION["net_i2_min_rate"] = int(current_state[4] / 1000)
                DEFAULT_ALLOCATION["net_i2_max_rate"] = int(current_state[5] / 1000)
            else:
                DEFAULT_ALLOCATION["net_share"] = 1
                DEFAULT_ALLOCATION["net_min_rate"] = int(bwlimit.bwmin / 1000)
                DEFAULT_ALLOCATION["net_max_rate"] = int(bwlimit.bwmax / 1000)
                DEFAULT_ALLOCATION["net_i2_min_rate"] = int(bwlimit.bwmin / 1000)
                DEFAULT_ALLOCATION["net_i2_max_rate"] = int(bwlimit.bwmax / 1000)

            DEFAULT_ALLOCATION["%s" % tag] = int(value)

            logger.log("bwmon: Updating %s: Min Rate = %d" % (slice, DEFAULT_ALLOCATION["net_min_rate"]))
            logger.log("bwmon: Updating %s: Max Rate = %d" % (slice, DEFAULT_ALLOCATION["net_max_rate"]))
            logger.log("bwmon: Updating %s: Min i2 Rate = %d" % (slice, DEFAULT_ALLOCATION["net_i2_min_rate"]))
            logger.log("bwmon: Updating %s: Max i2 Rate = %d" % (slice, DEFAULT_ALLOCATION["net_i2_max_rate"]))
            logger.log("bwmon: Updating %s: Net Share = %d" % (slice, DEFAULT_ALLOCATION["net_share"]))

            bwlimit.set(xid = slice_xid,
                 minrate = DEFAULT_ALLOCATION["net_min_rate"] * 1000,
                 maxrate = DEFAULT_ALLOCATION["net_max_rate"] * 1000,
                 minexemptrate = DEFAULT_ALLOCATION["net_i2_min_rate"] * 1000,
                 maxexemptrate = DEFAULT_ALLOCATION["net_i2_max_rate"] * 1000,
                 share = DEFAULT_ALLOCATION["net_share"])

            # FIXME: bwmon daemon?
            #default_MaxKByte = 10546875
            #default_Maxi2KByte = 31640625
            #ThreshKByte = MaxKByte * .8
            #Threshi2KByte = Maxi2KByte * .8
            #             logger.log("bwmon: Updating %s: Max KByte lim = %s" %(self.name, self.MaxKByte))
            #             logger.log("bwmon: Updating %s: Max i2 KByte = %s" %(self.name, self.Maxi2KByte))
            #             logger.log("bwmon: Updating %s: Thresh KByte = %s" %(self.name, self.ThreshKByte))
            #             logger.log("bwmon: Updating %s: i2 Thresh KByte = %s" %(self.name, self.Threshi2KByte))
            # Not Used
            #             logger.log("bwmon: Updating %s: Net i2 Share = %s" %(self.name, self.i2Share))

        return True


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

        if tag == "cpu_share":
            logger.log("cpu_share: Removing cpu_share value %s from %s slice" % (value, slice))

            DEFAULT = 1
            vserver_instance.set_sched_config(0, DEFAULT)

        if tag == "disk_max":
            logger.log("disk_max: Removing disk_max value %s from %s slice" % (value, slice))

            logger.log("disk_max: %s: computing disk usage: beginning" % slice)
            vserver_instance.init_disk_info()
            logger.log("disk_max: %s: computing disk usage: ended" % slice)

            DEFAULT = 100000000
            logger.log("disk_max: %s: setting max disk usage to %s KiB" % (slice, DEFAULT))
            vserver_instance.set_disklimit(max(int(DEFAULT), vserver_instance.disk_blocks))

        if tag == "capabilities":
            logger.log("capabilities: Removing capabilities value %s from slice %s" % (value, slice))

            DEFAULT = ""
            vserver_instance.set_capabilities_config(DEFAULT)

        if tag == "ip_addresses":
            logger.log("ip_addresses: Removing ip_addresses value %s from %s" % (value, slice))

            DEFAULT = "0.0.0.0"
            vserver_instance.set_ipaddresses_config(DEFAULT)

        if tag == "enabled":
            logger.log("enabled: Removing enabled value %s from slice %s" % (value, slice))

            vserver_instance.start()

#        if tag == "initscript":
#            logger.log("initscript: Removing %s slice with initscript value %s" % (slice, value[0]["name"]))

#            vinit = open("/usr/share/NodeManager/sliver-initscripts/vinit").readlines()
#            self.__writeToFile__("/vservers/%s/etc/rc.d/init.d/vinit" % slice, vinit, False)
#            os.chmod("/vservers/%s/etc/rc.d/init.d/vinit" % slice, 0755)

#            try:
#                os.symlink("../init.d/vinit", "/vservers/%s/etc/rc.d/rc3.d/S99vinit" % slice)
#            except OSError:
#                pass

#            os.unlink("/vservers/%s/etc/rc.d/init.d/vinit.slice" % slice)

#            if value[0]["enabled"] == True:
#                logger.log("initscript: Stoping %s slice with initscript value %s" % (slice, value[0]["name"]))

        if tag.endswith("_min") or tag.endswith("_soft") or tag.endswith("_hard"):
            logger.log("rlimit: Removing rlimit %s with value %s from slice %s" % (tag, value, slice))

            # special constant that tells vserver to keep its existing settings
            KEEP_LIMIT = vserver.VC_LIM_KEEP
            INFINITY = vserver.VC_LIM_INFINITY

            # populate the sliver/vserver specific default allocations table,
            # which is used to look for slice attributes
            DEFAULT_ALLOCATION = {}

            rlimit = tag.split("_")[0]
            DEFAULT_ALLOCATION["%s_min" % rlimit] = KEEP_LIMIT
            DEFAULT_ALLOCATION["%s_soft" % rlimit] = KEEP_LIMIT
            DEFAULT_ALLOCATION["%s_hard" % rlimit] = KEEP_LIMIT

            DEFAULT_ALLOCATION["%s" % tag] = INFINITY

            update = vserver_instance.set_rlimit(rlimit.upper(),
                            DEFAULT_ALLOCATION["%s_hard" % rlimit],
                            DEFAULT_ALLOCATION["%s_soft" % rlimit],
                            DEFAULT_ALLOCATION["%s_min" % rlimit])

            if update:
                logger.log("rlimit: setting rlimit %s to (%s, %s, %s)" %
                            (rlimit.upper(),
                            DEFAULT_ALLOCATION["%s_hard" % rlimit],
                            DEFAULT_ALLOCATION["%s_soft" % rlimit],
                            DEFAULT_ALLOCATION["%s_min" % rlimit]))

        if tag.startswith("net_"):
            logger.log("bwlimit: Removing bwlimit %s to %s slice with %s value" % (tag, slice, value))

        return True
