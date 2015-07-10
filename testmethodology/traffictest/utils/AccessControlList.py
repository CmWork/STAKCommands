from StcIntPythonPL import *
import spirent.core.utils.IfUtils as If
import os
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mmutils


class AccessControlEntry:
    '''
    The AccessControlEntry, or ACE for short, holds all of the information necessary
    to form packets to either conform to the ACE or not conform to the ACE. A single
    ACE can be used to create multiple packet information (e.g., increasing
    MAC addresses, decreasing IP addresses, etc.).

    The ACE is also aware of what kinds of packet information to form from the rules
    that it holds. conform_to_accept determines if the packets should conform to the
    Action ACCEPT and not conform to the Action DENY, or visa-versa. This feature is
    intended to be used by the parent processes to keep packet information grouped
    (e.g., by tag) based upon whether they are intended to be blocked by the DUT or
    to pass through the DUT under ideal conditions.
    '''
    def __init__(self, conform_to_accept, keys, rule_content):
        self.error = ''
        self.last_dstmac = None
        self.last_srcmac = None
        self.last_dstip = None
        self.last_srcip = None
        self.last_dstport = None
        self.last_srcport = None
        self.conform_to_accept = conform_to_accept
        self.keys = keys
        self.dict = {}
        values = rule_content.split(',')
        if len(keys) != len(values):
            self.error = 'Rules file is invalid, key and value counts are not the same.'
            return
        for i in range(0, len(keys)):
            self.dict[keys[i]] = values[i].replace(' ', '')
        self.to_conform = self.is_accept() == self.conform_to_accept
        if self.dict['L4Type'] != 'TCP':
            self.error = 'Only TCP is supported at this time.'
        return

    def is_accept(self):
        return self.dict['Action'].upper() == 'ACCEPT'

    def dst_ip(self):
        self.last_dstip = self.ip('DstIPAddr', self.last_dstip)
        return self.last_dstip

    def src_ip(self):
        self.last_srcip = self.ip('SrcIPAddr', self.last_srcip)
        return self.last_srcip

    def dst_mac(self):
        self.last_dstmac = self.mac('DstMAC', self.last_dstmac)
        return self.last_dstmac

    def src_mac(self):
        self.last_srcmac = self.mac('SrcMAC', self.last_srcmac)
        return self.last_srcmac

    def dst_port(self):
        self.last_dstport = self.port('DstPort', self.last_dstport)
        return self.last_dstport

    def src_port(self):
        self.last_srcport = self.port('SrcPort', self.last_srcport)
        return self.last_srcport

    def port(self, key, last):
        port_val = self.dict[key] if last is None else last
        if port_val == 'ANY' or port_val == '':
            return ''
        op = self.dict[key + 'Op']
        if op.find('=') > -1:
            return self.dict[key]
        if op == '>' and self.to_conform or op == '<' and not self.to_conform:
            return str(int(port_val) + 1)
        elif op == '<' and self.to_conform or op == '>' and not self.to_conform:
            return str(int(port_val) - 1)
        else:
            error(self, 'port', ' unknown operator "' + op + '"')
        return ''

    def mac(self, key, last):
        mac_val = self.dict[key] if last is None else last
        if mac_val == 'ANY' or mac_val == '':
            return ''
        op = self.dict[key + 'Op']
        if op.find('=') > -1:
            return self.dict[key]
        if op == '>' and self.to_conform or op == '<' and not self.to_conform:
            return If.GetNextMacAddress(mac_val, 48, 1, 1)
        elif op == '<' and self.to_conform or op == '>' and not self.to_conform:
            return If.GetPrevMacAddress(mac_val, 48, 1, 1)
        else:
            error(self, 'mac', ' unknown operator "' + op + '"')
        return ''

    def ip(self, key, last):
        ip_val = self.dict[key] if last is None else last
        if ip_val == 'ANY' or ip_val == '':
            return ''
        op = self.dict[key + 'Op']
        if op.find('=') > -1:
            return self.dict[key]
        if op == '>' and self.to_conform or op == '<' and not self.to_conform:
            return If.GetNextIPAddress(ip_val, '0.0.0.1', 1)
        elif op == '<' and self.to_conform or op == '>' and not self.to_conform:
            return If.GetPrevIPAddress(ip_val, '0.0.0.1', 1)
        else:
            error(self, 'ip', ' unknown operator "' + op + '"')
        return ''

    def error(self, proc, msg):
        self.error = msg
        plLogger = PLLogger.GetLogger('Methodology')
        plLogger.LogError('AccessControlEntry.' + proc + '(): ' + msg)
        return


class AccessControlList:
    '''
    The AccessControlList, or ACL for short, holds a complete import of access rules
    and implements each rule through its own corresponding AccessControlEntry object.
    The ACL object holds the collection of ACEs that are formed under its rules. All
    references to the ACEs for the set of rules are available through the reference
    to the ace_list() method.
    '''
    def __init__(self, conform_to_accept):
        self.conform_to_accept = conform_to_accept
        return

    def import_rules_file(self, rules_file):
        if not os.path.isfile(rules_file):
            found_file = mmutils.find_file_across_common_paths(rules_file)
            if found_file == '':
                return 'Unable to find rules file:' + rules_file
            rules_file = found_file
        with open(rules_file, 'r') as f:
            file_content = f.read()
        return self.import_content(file_content)

    def import_content(self, file_content):
        self.aces = []
        self.valid_keys = 'DstMACOp,DstMAC,SrcMACOp,SrcMAC,' \
            'DstIPAddrOp,DstIPAddr,SrcIPAddrOp,SrcIPAddr,' \
            'L4Type,DstPortOp,DstPort,SrcPortOp,SrcPort,Action' \
            .replace(' ', '').split(',')

        keys = []
        for line in file_content.split('\n'):
            line = line.replace(' ', '')
            if len(line) == 0:
                continue
            if len(keys) == 0:
                keys = line.split(',')
                if len(keys) != len(self.valid_keys):
                    return 'Rules file is invalid, key counts are incorrect.'
                for i in range(0, len(keys)):
                    if self.valid_keys[i] != keys[i]:
                        return 'Rules file is invalid, unknown key "' + keys[i] + '".'
                continue

            ace = AccessControlEntry(self.conform_to_accept, keys, line)
            msg = ace.error
            if msg != '':
                return msg
            self.aces.append(ace)
        return ''

    def count(self):
        return len(self.aces)

    def ace_list(self):
        return self.aces
