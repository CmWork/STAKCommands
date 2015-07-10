import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
from spirent.methodology.traffictest.utils.AccessControlList import *


def test_acl__init__():
    acl = AccessControlList(True)
    assert acl.conform_to_accept
    acl = AccessControlList(False)
    assert not acl.conform_to_accept
    return


def test_acl_import_content():
    acl = AccessControlList(True)
    msg = acl.import_content(good_rules1())
    assert msg == ''
    assert acl.count() == 2
    acl = AccessControlList(True)
    msg = acl.import_content(bad_rules1())
    assert msg != ''
    assert acl.count() == 0
    msg = acl.import_content(bad_rules2())
    assert msg != ''
    assert acl.count() == 1
    return


def test_ace__init__():
    ace = AccessControlEntry(True, keys1(), content1())
    assert ace is not None
    assert ace.error == ''
    assert ace.last_dstmac is None
    assert ace.last_srcmac is None
    assert ace.last_dstip is None
    assert ace.last_srcip is None
    assert ace.last_dstport is None
    assert ace.last_srcport is None
    assert ace.conform_to_accept
    assert ace.keys == keys1()
    assert len(ace.dict.keys()) == len(ace.keys)
    assert ace.is_accept()
    assert ace.to_conform
    return


def test_ace_dst_ip():
    ace = AccessControlEntry(True, keys1(), content1())
    assert ace.dst_ip() == '1.1.2.0'
    assert ace.last_dstip == '1.1.2.0'
    assert ace.dst_ip() == '1.1.2.1'
    assert ace.last_dstip == '1.1.2.1'
    assert ace.dst_ip() == '1.1.2.2'
    assert ace.last_dstip == '1.1.2.2'
    assert ace.last_srcip is None
    assert ace.last_dstmac is None
    assert ace.last_srcmac is None
    assert ace.last_dstport is None
    assert ace.last_srcport is None
    ace = AccessControlEntry(True, keys1(), content2())
    assert ace.dst_ip() == '1.1.1.254'
    assert ace.last_dstip == '1.1.1.254'
    assert ace.dst_ip() == '1.1.1.253'
    assert ace.last_dstip == '1.1.1.253'
    assert ace.dst_ip() == '1.1.1.252'
    assert ace.last_dstip == '1.1.1.252'
    assert ace.last_srcip is None
    assert ace.last_dstmac is None
    assert ace.last_srcmac is None
    assert ace.last_dstport is None
    assert ace.last_srcport is None
    return


def test_ace_src_ip():
    ace = AccessControlEntry(True, keys1(), content1())
    assert ace.src_ip() == '1.1.0.255'
    assert ace.last_srcip == '1.1.0.255'
    assert ace.src_ip() == '1.1.0.254'
    assert ace.last_srcip == '1.1.0.254'
    assert ace.src_ip() == '1.1.0.253'
    assert ace.last_srcip == '1.1.0.253'
    assert ace.last_dstip is None
    assert ace.last_dstmac is None
    assert ace.last_srcmac is None
    assert ace.last_dstport is None
    assert ace.last_srcport is None
    ace = AccessControlEntry(True, keys1(), content2())
    assert ace.src_ip() == '1.1.1.1'
    assert ace.last_srcip == '1.1.1.1'
    assert ace.src_ip() == '1.1.1.2'
    assert ace.last_srcip == '1.1.1.2'
    assert ace.src_ip() == '1.1.1.3'
    assert ace.last_srcip == '1.1.1.3'
    assert ace.last_dstip is None
    assert ace.last_dstmac is None
    assert ace.last_srcmac is None
    assert ace.last_dstport is None
    assert ace.last_srcport is None
    return


def test_ace_dst_mac():
    ace = AccessControlEntry(True, keys1(), content1())
    assert ace.dst_mac() == '00:00:40:00:01:00'
    assert ace.last_dstmac == '00:00:40:00:01:00'
    assert ace.dst_mac() == '00:00:40:00:01:01'
    assert ace.last_dstmac == '00:00:40:00:01:01'
    assert ace.dst_mac() == '00:00:40:00:01:02'
    assert ace.last_dstmac == '00:00:40:00:01:02'
    assert ace.last_srcip is None
    assert ace.last_dstip is None
    assert ace.last_srcmac is None
    assert ace.last_dstport is None
    assert ace.last_srcport is None
    ace = AccessControlEntry(True, keys1(), content2())
    assert ace.dst_mac() == '00:00:40:00:00:FE'
    assert ace.last_dstmac == '00:00:40:00:00:FE'
    assert ace.dst_mac() == '00:00:40:00:00:FD'
    assert ace.last_dstmac == '00:00:40:00:00:FD'
    assert ace.dst_mac() == '00:00:40:00:00:FC'
    assert ace.last_dstmac == '00:00:40:00:00:FC'
    assert ace.last_srcip is None
    assert ace.last_dstip is None
    assert ace.last_srcmac is None
    assert ace.last_dstport is None
    assert ace.last_srcport is None
    return


def test_ace_src_mac():
    ace = AccessControlEntry(True, keys1(), content1())
    assert ace.src_mac() == '00:00:50:00:00:FF'
    assert ace.last_srcmac == '00:00:50:00:00:FF'
    assert ace.src_mac() == '00:00:50:00:00:FE'
    assert ace.last_srcmac == '00:00:50:00:00:FE'
    assert ace.src_mac() == '00:00:50:00:00:FD'
    assert ace.last_srcmac == '00:00:50:00:00:FD'
    assert ace.last_srcip is None
    assert ace.last_dstip is None
    assert ace.last_dstmac is None
    assert ace.last_dstport is None
    assert ace.last_srcport is None
    ace = AccessControlEntry(True, keys1(), content2())
    assert ace.src_mac() == '00:00:50:00:01:01'
    assert ace.last_srcmac == '00:00:50:00:01:01'
    assert ace.src_mac() == '00:00:50:00:01:02'
    assert ace.last_srcmac == '00:00:50:00:01:02'
    assert ace.src_mac() == '00:00:50:00:01:03'
    assert ace.last_srcmac == '00:00:50:00:01:03'
    assert ace.last_srcip is None
    assert ace.last_dstip is None
    assert ace.last_dstmac is None
    assert ace.last_dstport is None
    assert ace.last_srcport is None
    return


def test_ace_dst_port():
    ace = AccessControlEntry(True, keys1(), content1())
    assert ace.dst_port() == '45'
    assert ace.last_dstport == '45'
    assert ace.dst_port() == '46'
    assert ace.last_dstport == '46'
    assert ace.dst_port() == '47'
    assert ace.last_dstport == '47'
    assert ace.last_srcip is None
    assert ace.last_dstip is None
    assert ace.last_srcmac is None
    assert ace.last_dstmac is None
    assert ace.last_srcport is None
    ace = AccessControlEntry(True, keys1(), content2())
    assert ace.dst_port() == '43'
    assert ace.last_dstport == '43'
    assert ace.dst_port() == '42'
    assert ace.last_dstport == '42'
    assert ace.dst_port() == '41'
    assert ace.last_dstport == '41'
    assert ace.last_srcip is None
    assert ace.last_dstip is None
    assert ace.last_srcmac is None
    assert ace.last_dstmac is None
    assert ace.last_srcport is None
    return


def test_ace_src_port():
    ace = AccessControlEntry(True, keys1(), content1())
    assert ace.src_port() == '21'
    assert ace.last_srcport == '21'
    assert ace.src_port() == '20'
    assert ace.last_srcport == '20'
    assert ace.src_port() == '19'
    assert ace.last_srcport == '19'
    assert ace.last_srcip is None
    assert ace.last_dstip is None
    assert ace.last_srcmac is None
    assert ace.last_dstmac is None
    assert ace.last_dstport is None
    ace = AccessControlEntry(True, keys1(), content2())
    assert ace.src_port() == '56'
    assert ace.last_srcport == '56'
    assert ace.src_port() == '57'
    assert ace.last_srcport == '57'
    assert ace.src_port() == '58'
    assert ace.last_srcport == '58'
    assert ace.last_srcip is None
    assert ace.last_dstip is None
    assert ace.last_srcmac is None
    assert ace.last_dstmac is None
    assert ace.last_dstport is None
    return


def keys1():
    return 'DstMACOp,DstMAC,SrcMACOp,SrcMAC,' \
           'DstIPAddrOp,DstIPAddr,SrcIPAddrOp,SrcIPAddr,' \
           'L4Type,DstPortOp,DstPort,SrcPortOp,SrcPort,Action' \
           .replace(' ', '').split(',')


def content1():
    return '>,00:00:40:00:00:FF,<,00:00:50:00:01:00,>,1.1.1.255,<,1.1.1.0,TCP,>,44,<,22,ACCEPT'


def content2():
    return '>,00:00:40:00:00:FF,<,00:00:50:00:01:00,>,1.1.1.255,<,1.1.1.0,TCP,>,44,<,55,DENY'


def good_rules1():
    return 'DstMACOp,DstMAC,SrcMACOp,SrcMAC,' \
           'DstIPAddrOp,DstIPAddr,SrcIPAddrOp,SrcIPAddr,' \
           'L4Type,DstPortOp,DstPort,SrcPortOp,SrcPort,Action\n' \
           '>,00:00:40:00:00:FE,<,00:00:50:00:01:00,>,1.1.1.255,<,1.1.1.0,TCP,,,,,ACCEPT\n' \
           '>,00:00:40:00:01:01,<,00:00:50:00:01:00,>,1.1.1.255,<,1.1.1.0,TCP,,,,,DENY\n'


def bad_rules1():
    # This content has a misspelled key...
    return 'DstMACOp,DstMAC,SrcMACOp,SrcMAC,' \
           'DstIPAddrOp,DstIPAddr,SrcIPAddrOp,SrcIPAddr,' \
           'DstPortOp,DstPort,SrcPortOp,SrcPort,Action\n' \
           '>,00:00:40:00:00:FF,<,00:00:50:00:01:00,>,1.1.1.255,<,1.1.1.0,TCP,,,ACCEPT\n' \
           '>,00:00:40:00:00:FF,<,00:00:50:00:01:00,>,1.1.1.255,<,1.1.1.0,TCP,,,DENY\n'


def bad_rules2():
    # This content has a missing item in the second rule...
    return 'DstMACOp,DstMAC,SrcMACOp,SrcMAC,' \
           'DstIPAddrOp,DstIPAddr,SrcIPAddrOp,SrcIPAddr,' \
           'L4Type,DstPortOp,DstPort,SrcPortOp,SrcPort,Action\n' \
           '>,00:00:40:00:00:FF,<,00:00:50:00:01:00,>,1.1.1.255,<,1.1.1.0,TCP,,,,,ACCEPT\n' \
           '>,00:00:40:00:00:FF,<,00:00:50:00:01:00,>,1.1.1.255,<,1.1.1.0,TCP,,,,DENY\n'
