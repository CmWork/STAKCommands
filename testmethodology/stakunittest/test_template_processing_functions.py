from StcIntPythonPL import *
import sys
import os
import json
import xml.etree.ElementTree as etree
sys.path.append(os.path.join(os.getcwd(), "STAKCommands",
                             "spirent", "methodology"))
import spirent.methodology.utils.template_processing_functions as proc_func


def test_get_modify_objects(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    tmpl = ctor.Create("StmTemplateConfig", project)

    # Create a Tag
    tags = project.GetObject("Tags")
    assert tags
    vlan_tag = ctor.Create("Tag", tags)
    vlan_tag.Set("Name", "ttVlanIf")
    dev_tag = ctor.Create("Tag", tags)
    dev_tag.Set("Name", "ttEmulatedDevice")

    # Create some ports
    port1 = ctor.Create("Port", project)
    port2 = ctor.Create("Port", project)

    # Create some generated VLANs and EmulatedDevices
    dev1 = ctor.Create("EmulatedDevice", project)
    dev1.AddObject(port1, RelationType("AffiliationPort"))
    vlan1 = ctor.Create("VlanIf", dev1)
    vlan1.AddObject(vlan_tag, RelationType("UserTag"))

    dev2 = ctor.Create("EmulatedDevice", project)
    dev2.AddObject(port2, RelationType("AffiliationPort"))
    vlan21 = ctor.Create("VlanIf", dev2)
    vlan22 = ctor.Create("VlanIf", dev2)
    vlan22.AddObject(vlan_tag, RelationType("UserTag"))

    dev3 = ctor.Create("EmulatedDevice", project)
    dev3.AddObject(port2, RelationType("AffiliationPort"))
    vlan31 = ctor.Create("VlanIf", dev3)
    vlan31.AddObject(vlan_tag, RelationType("UserTag"))
    vlan32 = ctor.Create("VlanIf", dev3)
    vlan32.AddObject(vlan_tag, RelationType("UserTag"))

    dev4 = ctor.Create("EmulatedDevice", project)
    dev4.AddObject(port1, RelationType("AffiliationPort"))

    for dev in [dev1, dev2, dev3, dev4]:
        tmpl.AddObject(dev, RelationType("GeneratedObject"))

    # Absent class, non-existent tag
    res = proc_func.get_modify_objects(tmpl, "Ipv4If", "ttIpv4If")
    assert res == {}

    # Present class, existent tag (not tagging anything)
    res = proc_func.get_modify_objects(tmpl, "VlanIf", "ttEmulatedDevice")
    assert res == {}

    # Absent class, existent tag (not tagging anything)
    res = proc_func.get_modify_objects(tmpl, "Ipv4If", "ttEmulatedDevice")
    assert res == {}

    # Absent class, existent tag (tagging something)
    res = proc_func.get_modify_objects(tmpl, "Ipv4If", "ttVlanIf")
    assert res == {}

    # Present class, existent tag (tagging something)
    res = proc_func.get_modify_objects(tmpl, "VlanIf", "ttVlanIf")
    assert len(res.keys()) == 2
    assert port1.GetObjectHandle() in res.keys()
    assert port2.GetObjectHandle() in res.keys()
    port1_obj_list = res[port1.GetObjectHandle()]
    assert len(port1_obj_list) == 1
    hnd_list = [obj.GetObjectHandle() for obj in port1_obj_list]
    assert vlan1.GetObjectHandle() in hnd_list

    port2_obj_list = res[port2.GetObjectHandle()]
    assert len(port2_obj_list) == 3
    hnd_list = [obj.GetObjectHandle() for obj in port2_obj_list]
    assert vlan22.GetObjectHandle() in hnd_list
    assert vlan31.GetObjectHandle() in hnd_list
    assert vlan32.GetObjectHandle() in hnd_list
    assert vlan21.GetObjectHandle() not in hnd_list

    # Check object sorting (based on handle)
    exp_hnd_list = sorted([vlan22.GetObjectHandle(),
                           vlan31.GetObjectHandle(),
                           vlan32.GetObjectHandle()])
    assert hnd_list == exp_hnd_list


def test_build_parameter_range_list():
    # Collections (count > 1)
    # Count == list param length
    res = proc_func.build_range_parameter_list(True, [1, 2, 3],
                                               count=3)
    assert res == [1, 2, 3]
    # Count > list param length
    res = proc_func.build_range_parameter_list(True, ["1", "2", "3"],
                                               count=5)
    assert res == ["1", "2", "3", "1", "2"]
    # Count < list param length
    res = proc_func.build_range_parameter_list(True, [1, 2, 3, 4, 5],
                                               count=2)
    assert res == [1, 2]
    # List param specified, count == 1 (default)
    res = proc_func.build_range_parameter_list(True, [1, 2, 3])
    assert res == [1]


def test_handle_uint_range_update_scalar(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "Dev")
    tags.AddObject(tag, RelationType("UserTag"))

    port1 = ctor.Create("Port", project)
    dev11 = ctor.Create("EmulatedDevice", project)
    dev12 = ctor.Create("EmulatedDevice", project)
    port2 = ctor.Create("Port", project)
    dev21 = ctor.Create("EmulatedDevice", project)
    dev22 = ctor.Create("EmulatedDevice", project)
    dev23 = ctor.Create("EmulatedDevice", project)
    port3 = ctor.Create("Port", project)
    dev31 = ctor.Create("EmulatedDevice", project)
    dev32 = ctor.Create("EmulatedDevice", project)
    dev33 = ctor.Create("EmulatedDevice", project)

    for dev in [dev11, dev12]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port1, RelationType("AffiliationPort"))
    for dev in [dev21, dev22, dev23]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port2, RelationType("AffiliationPort"))
    for dev in [dev31, dev32, dev33]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port3, RelationType("AffiliationPort"))

    # Build the target_dict.  Note that dev32 is skipped.
    target_dict = {}
    target_dict[port1.GetObjectHandle()] = [dev11, dev12]
    target_dict[port2.GetObjectHandle()] = [dev21, dev22, dev23]
    target_dict[port3.GetObjectHandle()] = [dev31, dev33]

    # Test reset=True, target_step
    proc_func.handle_uint_range_update(
        target_dict,
        ["30"], ["2"],
        [1], [0],
        ["10"], True,
        "EmulatedDevice", "DeviceCount")
    assert dev11.Get("DeviceCount") == 30
    assert dev12.Get("DeviceCount") == 30
    assert dev21.Get("DeviceCount") == 40
    assert dev22.Get("DeviceCount") == 40
    assert dev23.Get("DeviceCount") == 42
    assert dev31.Get("DeviceCount") == 50
    assert dev32.Get("DeviceCount") == 1
    assert dev33.Get("DeviceCount") == 50

    # Test reset=False, target_step
    proc_func.handle_uint_range_update(
        target_dict,
        ["30"], ["2"],
        [0], [0],
        ["10"], False,
        "EmulatedDevice", "DeviceCount")
    assert dev11.Get("DeviceCount") == 30
    assert dev12.Get("DeviceCount") == 32
    assert dev21.Get("DeviceCount") == 44
    assert dev22.Get("DeviceCount") == 46
    assert dev23.Get("DeviceCount") == 48
    assert dev31.Get("DeviceCount") == 60
    assert dev32.Get("DeviceCount") == 1
    assert dev33.Get("DeviceCount") == 62

    # Test reset=True, target_step=0
    proc_func.handle_uint_range_update(
        target_dict,
        ["30"], ["2"],
        [0], [0],
        [0], True,
        "EmulatedDevice", "DeviceCount")
    assert dev11.Get("DeviceCount") == 30
    assert dev12.Get("DeviceCount") == 32
    assert dev21.Get("DeviceCount") == 30
    assert dev22.Get("DeviceCount") == 32
    assert dev23.Get("DeviceCount") == 34
    assert dev31.Get("DeviceCount") == 30
    assert dev32.Get("DeviceCount") == 1
    assert dev33.Get("DeviceCount") == 32

    # Test reset=False, target_step=0 (original behavior)
    proc_func.handle_uint_range_update(
        target_dict,
        ["30"], ["2"],
        [0], [0],
        ["0"], False,
        "EmulatedDevice", "DeviceCount")
    assert dev11.Get("DeviceCount") == 30
    assert dev12.Get("DeviceCount") == 32
    assert dev21.Get("DeviceCount") == 34
    assert dev22.Get("DeviceCount") == 36
    assert dev23.Get("DeviceCount") == 38
    assert dev31.Get("DeviceCount") == 40
    assert dev32.Get("DeviceCount") == 1
    assert dev33.Get("DeviceCount") == 42

    # Rebuild the target_dict (order matters)
    target_dict = {}
    target_dict[port1.GetObjectHandle()] = [dev12, dev11]
    target_dict[port2.GetObjectHandle()] = [dev23, dev22, dev21]
    target_dict[port3.GetObjectHandle()] = [dev32, dev31, dev33]

    proc_func.handle_uint_range_update(
        target_dict,
        ["30"], ["2"],
        [0], [0],
        ["0"], False,
        "EmulatedDevice", "DeviceCount")
    assert dev11.Get("DeviceCount") == 32
    assert dev12.Get("DeviceCount") == 30
    assert dev21.Get("DeviceCount") == 38
    assert dev22.Get("DeviceCount") == 36
    assert dev23.Get("DeviceCount") == 34
    assert dev31.Get("DeviceCount") == 42
    assert dev32.Get("DeviceCount") == 40
    assert dev33.Get("DeviceCount") == 44


def test_handle_uint_range_update_collection(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "Dev")
    tags.AddObject(tag, RelationType("UserTag"))
    vlan_tag = ctor.Create("Tag", tags)
    tag.Set("Name", "Vlan")
    tags.AddObject(tag, RelationType("UserTag"))

    # Create stuff
    port1 = ctor.Create("Port", project)
    dev11 = ctor.Create("EmulatedDevice", project)
    dev12 = ctor.Create("EmulatedDevice", project)
    port2 = ctor.Create("Port", project)
    dev21 = ctor.Create("EmulatedDevice", project)
    dev22 = ctor.Create("EmulatedDevice", project)
    dev23 = ctor.Create("EmulatedDevice", project)
    port3 = ctor.Create("Port", project)
    dev31 = ctor.Create("EmulatedDevice", project)
    dev32 = ctor.Create("EmulatedDevice", project)
    dev33 = ctor.Create("EmulatedDevice", project)

    for dev in [dev11, dev12]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port1, RelationType("AffiliationPort"))
    for dev in [dev21, dev22, dev23]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port2, RelationType("AffiliationPort"))
    for dev in [dev31, dev32, dev33]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port3, RelationType("AffiliationPort"))

    # Create VLANs.  Done in reverse order to demonstrate
    # creation order matters when applying modifiers.
    vlan331 = ctor.Create("VlanIf", dev33)
    vlan321 = ctor.Create("VlanIf", dev32)
    vlan311 = ctor.Create("VlanIf", dev31)
    vlan312 = ctor.Create("VlanIf", dev31)
    vlan231 = ctor.Create("VlanIf", dev23)
    vlan221 = ctor.Create("VlanIf", dev22)
    vlan121 = ctor.Create("VlanIf", dev12)
    vlan111 = ctor.Create("VlanIf", dev11)
    vlan112 = ctor.Create("VlanIf", dev11)

    # Tag the VLANs.  Skipping vlan221
    for vlan in [vlan331, vlan321, vlan311, vlan312, vlan231,
                 vlan121, vlan111, vlan112]:
        vlan.AddObject(vlan_tag, RelationType("UserTag"))

    # Build the target_dict.  Note that vlan321 is skipped.
    target_dict = {}
    target_dict[port1.GetObjectHandle()] = [vlan111, vlan112, vlan121]
    target_dict[port2.GetObjectHandle()] = [vlan231]
    target_dict[port3.GetObjectHandle()] = [vlan311, vlan312, vlan331]

    # Set defaults for VLANs that aren't being modified
    vlan321.SetCollection("IdList", [1234, 1235])
    vlan221.SetCollection("IdList", [1234, 1235])

    # Test reset=True, target_step
    proc_func.handle_uint_range_update(
        target_dict,
        ["100", "400"], ["5", "10"],
        [1, 0], [0, 0],
        ["1000", "1000"], True,
        "VlanIf", "IdList")

    # VLAN creation order (based on port (target) creation order
    # and target_dict sorted order:
    # 111, 112, 121, (221), 231, 311, 312, (321), 331
    assert vlan111.GetCollection("IdList") == [100, 400]
    assert vlan112.GetCollection("IdList") == [100, 410]
    assert vlan121.GetCollection("IdList") == [105, 420]
    assert vlan221.GetCollection("IdList") == [1234, 1235]
    assert vlan231.GetCollection("IdList") == [1100, 1400]
    assert vlan311.GetCollection("IdList") == [2100, 2400]
    assert vlan312.GetCollection("IdList") == [2100, 2410]
    assert vlan321.GetCollection("IdList") == [1234, 1235]
    assert vlan331.GetCollection("IdList") == [2105, 2420]

    # Test reset=False, target_step
    proc_func.handle_uint_range_update(
        target_dict,
        ["100", "400"], ["5", "10"],
        [0, 0], [0, 0],
        ["1000", "1000"], False,
        "VlanIf", "IdList")

    # VLAN creation order (based on port (target) creation order
    # and target_dict sorted order:
    # 111, 112, 121, (221), 231, 311, 312, (321), 331
    assert vlan111.GetCollection("IdList") == [100, 400]
    assert vlan112.GetCollection("IdList") == [105, 410]
    assert vlan121.GetCollection("IdList") == [110, 420]
    assert vlan221.GetCollection("IdList") == [1234, 1235]
    assert vlan231.GetCollection("IdList") == [1115, 1430]
    assert vlan311.GetCollection("IdList") == [2120, 2440]
    assert vlan312.GetCollection("IdList") == [2125, 2450]
    assert vlan321.GetCollection("IdList") == [1234, 1235]
    assert vlan331.GetCollection("IdList") == [2130, 2460]

    # Test reset=True, target_step=0
    proc_func.handle_uint_range_update(
        target_dict,
        ["100", "400"], ["5", "10"],
        [0, 0], [0, 0],
        ["0", "0"], True,
        "VlanIf", "IdList")

    # VLAN creation order (based on port (target) creation order
    # and target_dict sorted order:
    # 111, 112, 121, (221), 231, 311, 312, (321), 331
    assert vlan111.GetCollection("IdList") == [100, 400]
    assert vlan112.GetCollection("IdList") == [105, 410]
    assert vlan121.GetCollection("IdList") == [110, 420]
    assert vlan221.GetCollection("IdList") == [1234, 1235]
    assert vlan231.GetCollection("IdList") == [100, 400]
    assert vlan311.GetCollection("IdList") == [100, 400]
    assert vlan312.GetCollection("IdList") == [105, 410]
    assert vlan321.GetCollection("IdList") == [1234, 1235]
    assert vlan331.GetCollection("IdList") == [110, 420]

    # Test reset=False, target_step=0 (original behavior)
    proc_func.handle_uint_range_update(
        target_dict,
        ["100", "400"], ["5", "10"],
        [0, 0], [0, 0],
        ["0", "0"], False,
        "VlanIf", "IdList")

    # VLAN creation order (based on port (target) creation order
    # and target_dict sorted order:
    # 111, 112, 121, (221), 231, 311, 312, (321), 331
    assert vlan111.GetCollection("IdList") == [100, 400]
    assert vlan112.GetCollection("IdList") == [105, 410]
    assert vlan121.GetCollection("IdList") == [110, 420]
    assert vlan221.GetCollection("IdList") == [1234, 1235]
    assert vlan231.GetCollection("IdList") == [115, 430]
    assert vlan311.GetCollection("IdList") == [120, 440]
    assert vlan312.GetCollection("IdList") == [125, 450]
    assert vlan321.GetCollection("IdList") == [1234, 1235]
    assert vlan331.GetCollection("IdList") == [130, 460]


def test_handle_ip_range_update_ipv4_scalar(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "Dev")
    tags.AddObject(tag, RelationType("UserTag"))
    ip_tag = ctor.Create("Tag", tags)
    ip_tag.Set("Name", "Ipv4If")
    tags.AddObject(tag, RelationType("UserTag"))

    port1 = ctor.Create("Port", project)
    dev11 = ctor.Create("EmulatedDevice", project)
    dev12 = ctor.Create("EmulatedDevice", project)
    port2 = ctor.Create("Port", project)
    dev21 = ctor.Create("EmulatedDevice", project)
    dev22 = ctor.Create("EmulatedDevice", project)
    dev23 = ctor.Create("EmulatedDevice", project)
    port3 = ctor.Create("Port", project)
    dev31 = ctor.Create("EmulatedDevice", project)
    dev32 = ctor.Create("EmulatedDevice", project)
    dev33 = ctor.Create("EmulatedDevice", project)

    for dev in [dev11, dev12]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port1, RelationType("AffiliationPort"))
    for dev in [dev21, dev22, dev23]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port2, RelationType("AffiliationPort"))
    for dev in [dev31, dev32, dev33]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port3, RelationType("AffiliationPort"))

    ip11 = ctor.Create("Ipv4If", dev11)
    ip12 = ctor.Create("Ipv4If", dev12)
    ip21 = ctor.Create("Ipv4If", dev21)
    ip22 = ctor.Create("Ipv4If", dev22)
    ip23 = ctor.Create("Ipv4If", dev23)
    ip31 = ctor.Create("Ipv4If", dev31)
    ip32 = ctor.Create("Ipv4If", dev32)
    ip33 = ctor.Create("Ipv4If", dev33)

    for ip in [ip11, ip12, ip21, ip22, ip23, ip31, ip32, ip33]:
        ip.AddObject(ip_tag, RelationType("UserTag"))

    # Build the target_dict.  Skip ip32
    target_dict = {}
    target_dict[port1.GetObjectHandle()] = [ip11, ip12]
    target_dict[port2.GetObjectHandle()] = [ip21, ip22, ip23]
    target_dict[port3.GetObjectHandle()] = [ip31, ip33]

    # Set ip32 to some default
    ip32.Set("Address", "5.5.5.5")

    # Test reset=True, target_step
    proc_func.handle_ip_range_update(
        target_dict,
        ["1.1.1.1"], ["0.0.1.0"],
        [0], [0],
        ["0.1.0.0"], True,
        "Ipv4If", "Address")
    assert ip11.Get("Address") == "1.1.1.1"
    assert ip12.Get("Address") == "1.1.2.1"
    assert ip21.Get("Address") == "1.2.1.1"
    assert ip22.Get("Address") == "1.2.2.1"
    assert ip23.Get("Address") == "1.2.3.1"
    assert ip31.Get("Address") == "1.3.1.1"
    assert ip32.Get("Address") == "5.5.5.5"
    assert ip33.Get("Address") == "1.3.2.1"

    # Test reset=False, target_step
    proc_func.handle_ip_range_update(
        target_dict,
        ["1.1.1.1"], ["0.0.1.0"],
        [0], [0],
        ["0.1.0.0"], False,
        "Ipv4If", "Address")
    assert ip11.Get("Address") == "1.1.1.1"
    assert ip12.Get("Address") == "1.1.2.1"
    assert ip21.Get("Address") == "1.2.3.1"
    assert ip22.Get("Address") == "1.2.4.1"
    assert ip23.Get("Address") == "1.2.5.1"
    assert ip31.Get("Address") == "1.3.6.1"
    assert ip32.Get("Address") == "5.5.5.5"
    assert ip33.Get("Address") == "1.3.7.1"

    # Test reset=True, target_step=0
    proc_func.handle_ip_range_update(
        target_dict,
        ["1.1.1.1"], ["0.0.1.0"],
        [0], [0],
        ["0.0.0.0"], True,
        "Ipv4If", "Address")
    assert ip11.Get("Address") == "1.1.1.1"
    assert ip12.Get("Address") == "1.1.2.1"
    assert ip21.Get("Address") == "1.1.1.1"
    assert ip22.Get("Address") == "1.1.2.1"
    assert ip23.Get("Address") == "1.1.3.1"
    assert ip31.Get("Address") == "1.1.1.1"
    assert ip32.Get("Address") == "5.5.5.5"
    assert ip33.Get("Address") == "1.1.2.1"

    # Test reset=False, target_step=0 (original behavior)
    proc_func.handle_ip_range_update(
        target_dict,
        ["1.1.1.1"], ["0.0.1.0"],
        [0], [0],
        ["0.0.0.0"], False,
        "Ipv4If", "Address")
    assert ip11.Get("Address") == "1.1.1.1"
    assert ip12.Get("Address") == "1.1.2.1"
    assert ip21.Get("Address") == "1.1.3.1"
    assert ip22.Get("Address") == "1.1.4.1"
    assert ip23.Get("Address") == "1.1.5.1"
    assert ip31.Get("Address") == "1.1.6.1"
    assert ip32.Get("Address") == "5.5.5.5"
    assert ip33.Get("Address") == "1.1.7.1"


def test_handle_ip_range_update_ipv4_collection(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "Dev")
    tags.AddObject(tag, RelationType("UserTag"))
    ip_tag = ctor.Create("Tag", tags)
    ip_tag.Set("Name", "Ipv4If")
    tags.AddObject(tag, RelationType("UserTag"))

    port1 = ctor.Create("Port", project)
    dev11 = ctor.Create("EmulatedDevice", project)
    dev12 = ctor.Create("EmulatedDevice", project)
    port2 = ctor.Create("Port", project)
    dev21 = ctor.Create("EmulatedDevice", project)
    dev22 = ctor.Create("EmulatedDevice", project)
    dev23 = ctor.Create("EmulatedDevice", project)
    port3 = ctor.Create("Port", project)
    dev31 = ctor.Create("EmulatedDevice", project)
    dev32 = ctor.Create("EmulatedDevice", project)
    dev33 = ctor.Create("EmulatedDevice", project)

    for dev in [dev11, dev12]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port1, RelationType("AffiliationPort"))
    for dev in [dev21, dev22, dev23]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port2, RelationType("AffiliationPort"))
    for dev in [dev31, dev32, dev33]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port3, RelationType("AffiliationPort"))

    ip11 = ctor.Create("Ipv4If", dev11)
    ip12 = ctor.Create("Ipv4If", dev12)
    ip21 = ctor.Create("Ipv4If", dev21)
    ip22 = ctor.Create("Ipv4If", dev22)
    ip23 = ctor.Create("Ipv4If", dev23)
    ip31 = ctor.Create("Ipv4If", dev31)
    ip32 = ctor.Create("Ipv4If", dev32)
    ip33 = ctor.Create("Ipv4If", dev33)

    for ip in [ip11, ip12, ip21, ip22, ip23, ip31, ip32, ip33]:
        ip.AddObject(ip_tag, RelationType("UserTag"))

    # Build the target_dict.  Skip ip32
    target_dict = {}
    target_dict[port1.GetObjectHandle()] = [ip11, ip12]
    target_dict[port2.GetObjectHandle()] = [ip21, ip22, ip23]
    target_dict[port3.GetObjectHandle()] = [ip31, ip33]

    # Set ip32 to some default
    ip32.SetCollection("AddrList", ["5.5.5.5", "6.6.6.6"])

    # Test reset=True, target_step
    proc_func.handle_ip_range_update(
        target_dict,
        ["1.0.0.0", "2.0.0.0"], ["0.0.1.0", "0.0.0.1"],
        [0, 0], [0, 0],
        ["0.1.0.0", "0.1.0.0"], True,
        "Ipv4If", "AddrList")
    assert ip11.GetCollection("AddrList") == ["1.0.0.0", "2.0.0.0"]
    assert ip12.GetCollection("AddrList") == ["1.0.1.0", "2.0.0.1"]
    assert ip21.GetCollection("AddrList") == ["1.1.0.0", "2.1.0.0"]
    assert ip22.GetCollection("AddrList") == ["1.1.1.0", "2.1.0.1"]
    assert ip23.GetCollection("AddrList") == ["1.1.2.0", "2.1.0.2"]
    assert ip31.GetCollection("AddrList") == ["1.2.0.0", "2.2.0.0"]
    assert ip32.GetCollection("AddrList") == ["5.5.5.5", "6.6.6.6"]
    assert ip33.GetCollection("AddrList") == ["1.2.1.0", "2.2.0.1"]

    # Test reset=False, target_step
    proc_func.handle_ip_range_update(
        target_dict,
        ["1.0.0.0", "2.0.0.0"], ["0.0.1.0", "0.0.0.1"],
        [0, 0], [0, 0],
        ["0.1.0.0", "0.1.0.0"], False,
        "Ipv4If", "AddrList")
    assert ip11.GetCollection("AddrList") == ["1.0.0.0", "2.0.0.0"]
    assert ip12.GetCollection("AddrList") == ["1.0.1.0", "2.0.0.1"]
    assert ip21.GetCollection("AddrList") == ["1.1.2.0", "2.1.0.2"]
    assert ip22.GetCollection("AddrList") == ["1.1.3.0", "2.1.0.3"]
    assert ip23.GetCollection("AddrList") == ["1.1.4.0", "2.1.0.4"]
    assert ip31.GetCollection("AddrList") == ["1.2.5.0", "2.2.0.5"]
    assert ip32.GetCollection("AddrList") == ["5.5.5.5", "6.6.6.6"]
    assert ip33.GetCollection("AddrList") == ["1.2.6.0", "2.2.0.6"]

    # Test reset=True, target_step=0
    proc_func.handle_ip_range_update(
        target_dict,
        ["1.0.0.0", "2.0.0.0"], ["0.0.1.0", "0.0.0.1"],
        [0, 0], [0, 0],
        ["0.0.0.0", "0.0.0.0"], True,
        "Ipv4If", "AddrList")
    assert ip11.GetCollection("AddrList") == ["1.0.0.0", "2.0.0.0"]
    assert ip12.GetCollection("AddrList") == ["1.0.1.0", "2.0.0.1"]
    assert ip21.GetCollection("AddrList") == ["1.0.0.0", "2.0.0.0"]
    assert ip22.GetCollection("AddrList") == ["1.0.1.0", "2.0.0.1"]
    assert ip23.GetCollection("AddrList") == ["1.0.2.0", "2.0.0.2"]
    assert ip31.GetCollection("AddrList") == ["1.0.0.0", "2.0.0.0"]
    assert ip32.GetCollection("AddrList") == ["5.5.5.5", "6.6.6.6"]
    assert ip33.GetCollection("AddrList") == ["1.0.1.0", "2.0.0.1"]

    # Test reset=False, target_step=0 (original behavior)
    proc_func.handle_ip_range_update(
        target_dict,
        ["1.0.0.0", "2.0.0.0"], ["0.0.1.0", "0.0.0.1"],
        [0, 0], [0, 0],
        ["0.0.0.0", "0.0.0.0"], False,
        "Ipv4If", "AddrList")
    assert ip11.GetCollection("AddrList") == ["1.0.0.0", "2.0.0.0"]
    assert ip12.GetCollection("AddrList") == ["1.0.1.0", "2.0.0.1"]
    assert ip21.GetCollection("AddrList") == ["1.0.2.0", "2.0.0.2"]
    assert ip22.GetCollection("AddrList") == ["1.0.3.0", "2.0.0.3"]
    assert ip23.GetCollection("AddrList") == ["1.0.4.0", "2.0.0.4"]
    assert ip31.GetCollection("AddrList") == ["1.0.5.0", "2.0.0.5"]
    assert ip32.GetCollection("AddrList") == ["5.5.5.5", "6.6.6.6"]
    assert ip33.GetCollection("AddrList") == ["1.0.6.0", "2.0.0.6"]


def test_handle_ip_range_update_ipv6_collection(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "Dev")
    tags.AddObject(tag, RelationType("UserTag"))
    ip_tag = ctor.Create("Tag", tags)
    ip_tag.Set("Name", "Ipv6If")
    tags.AddObject(tag, RelationType("UserTag"))

    port1 = ctor.Create("Port", project)
    dev11 = ctor.Create("EmulatedDevice", project)
    dev12 = ctor.Create("EmulatedDevice", project)
    port2 = ctor.Create("Port", project)
    dev21 = ctor.Create("EmulatedDevice", project)
    dev22 = ctor.Create("EmulatedDevice", project)
    dev23 = ctor.Create("EmulatedDevice", project)
    port3 = ctor.Create("Port", project)
    dev31 = ctor.Create("EmulatedDevice", project)
    dev32 = ctor.Create("EmulatedDevice", project)
    dev33 = ctor.Create("EmulatedDevice", project)

    for dev in [dev11, dev12]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port1, RelationType("AffiliationPort"))
    for dev in [dev21, dev22, dev23]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port2, RelationType("AffiliationPort"))
    for dev in [dev31, dev32, dev33]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port3, RelationType("AffiliationPort"))

    ip11 = ctor.Create("Ipv6If", dev11)
    ip12 = ctor.Create("Ipv6If", dev12)
    ip21 = ctor.Create("Ipv6If", dev21)
    ip22 = ctor.Create("Ipv6If", dev22)
    ip23 = ctor.Create("Ipv6If", dev23)
    ip31 = ctor.Create("Ipv6If", dev31)
    ip32 = ctor.Create("Ipv6If", dev32)
    ip33 = ctor.Create("Ipv6If", dev33)

    for ip in [ip11, ip12, ip21, ip22, ip23, ip31, ip32, ip33]:
        ip.AddObject(ip_tag, RelationType("UserTag"))

    # Build the target_dict.  Skip ip32
    target_dict = {}
    target_dict[port1.GetObjectHandle()] = [ip11, ip12]
    target_dict[port2.GetObjectHandle()] = [ip21, ip22, ip23]
    target_dict[port3.GetObjectHandle()] = [ip31, ip33]

    # Set ip32 to some default
    ip32.SetCollection("AddrList", ["5000::5", "6000::6"])

    # Test reset=True, target_step
    proc_func.handle_ip_range_update(
        target_dict,
        ["2015::15", "2020::20"], ["::1:0", "::0:1:0:0"],
        [0, 0], [0, 0],
        ["::1:0:0:0", "::1:0:0:0"], True,
        "Ipv6If", "AddrList")
    assert ip11.GetCollection("AddrList") == \
        ["2015::15", "2020::20"]
    assert ip12.GetCollection("AddrList") == \
        ["2015::1:15", "2020::1:0:20"]
    assert ip21.GetCollection("AddrList") == \
        ["2015::1:0:0:15", "2020::1:0:0:20"]
    assert ip22.GetCollection("AddrList") == \
        ["2015::1:0:1:15", "2020::1:1:0:20"]
    assert ip23.GetCollection("AddrList") == \
        ["2015::1:0:2:15", "2020::1:2:0:20"]
    assert ip31.GetCollection("AddrList") == \
        ["2015::2:0:0:15", "2020::2:0:0:20"]
    assert ip32.GetCollection("AddrList") == ["5000::5", "6000::6"]
    assert ip33.GetCollection("AddrList") == \
        ["2015::2:0:1:15", "2020::2:1:0:20"]

    # Test reset=False, target_step
    proc_func.handle_ip_range_update(
        target_dict,
        ["2015::15", "2020::20"], ["::1:0", "::0:1:0:0"],
        [0, 0], [0, 0],
        ["::1:0:0:0", "::1:0:0:0"], False,
        "Ipv6If", "AddrList")
    assert ip11.GetCollection("AddrList") == \
        ["2015::15", "2020::20"]
    assert ip12.GetCollection("AddrList") == \
        ["2015::1:15", "2020::1:0:20"]
    assert ip21.GetCollection("AddrList") == \
        ["2015::1:0:2:15", "2020::1:2:0:20"]
    assert ip22.GetCollection("AddrList") == \
        ["2015::1:0:3:15", "2020::1:3:0:20"]
    assert ip23.GetCollection("AddrList") == \
        ["2015::1:0:4:15", "2020::1:4:0:20"]
    assert ip31.GetCollection("AddrList") == \
        ["2015::2:0:5:15", "2020::2:5:0:20"]
    assert ip32.GetCollection("AddrList") == ["5000::5", "6000::6"]
    assert ip33.GetCollection("AddrList") == \
        ["2015::2:0:6:15", "2020::2:6:0:20"]

    # Test reset=True, target_step=0
    proc_func.handle_ip_range_update(
        target_dict,
        ["2015::15", "2020::20"], ["::1:0", "::0:1:0:0"],
        [0, 0], [0, 0],
        ["::", "0::0"], True,
        "Ipv6If", "AddrList")
    assert ip11.GetCollection("AddrList") == \
        ["2015::15", "2020::20"]
    assert ip12.GetCollection("AddrList") == \
        ["2015::1:15", "2020::1:0:20"]
    assert ip21.GetCollection("AddrList") == \
        ["2015::15", "2020::20"]
    assert ip22.GetCollection("AddrList") == \
        ["2015::1:15", "2020::1:0:20"]
    assert ip23.GetCollection("AddrList") == \
        ["2015::2:15", "2020::2:0:20"]
    assert ip31.GetCollection("AddrList") == \
        ["2015::15", "2020::20"]
    assert ip32.GetCollection("AddrList") == ["5000::5", "6000::6"]
    assert ip33.GetCollection("AddrList") == \
        ["2015::1:15", "2020::1:0:20"]

    # Test reset=False, target_step=0 (original behavior)
    proc_func.handle_ip_range_update(
        target_dict,
        ["2015::15", "2020::20"], ["::1:0", "::0:1:0:0"],
        [0, 0], [0, 0],
        ["::", "0::0"], False,
        "Ipv6If", "AddrList")
    assert ip11.GetCollection("AddrList") == \
        ["2015::15", "2020::20"]
    assert ip12.GetCollection("AddrList") == \
        ["2015::1:15", "2020::1:0:20"]
    assert ip21.GetCollection("AddrList") == \
        ["2015::2:15", "2020::2:0:20"]
    assert ip22.GetCollection("AddrList") == \
        ["2015::3:15", "2020::3:0:20"]
    assert ip23.GetCollection("AddrList") == \
        ["2015::4:15", "2020::4:0:20"]
    assert ip31.GetCollection("AddrList") == \
        ["2015::5:15", "2020::5:0:20"]
    assert ip32.GetCollection("AddrList") == ["5000::5", "6000::6"]
    assert ip33.GetCollection("AddrList") == \
        ["2015::6:15", "2020::6:0:20"]


def test_handle_mac_range_update_scalar(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "Dev")
    tags.AddObject(tag, RelationType("UserTag"))
    eth_tag = ctor.Create("Tag", tags)
    eth_tag.Set("Name", "EthIIIf")
    tags.AddObject(tag, RelationType("UserTag"))

    port1 = ctor.Create("Port", project)
    dev11 = ctor.Create("EmulatedDevice", project)
    dev12 = ctor.Create("EmulatedDevice", project)
    port2 = ctor.Create("Port", project)
    dev21 = ctor.Create("EmulatedDevice", project)
    dev22 = ctor.Create("EmulatedDevice", project)
    dev23 = ctor.Create("EmulatedDevice", project)
    port3 = ctor.Create("Port", project)
    dev31 = ctor.Create("EmulatedDevice", project)
    dev32 = ctor.Create("EmulatedDevice", project)
    dev33 = ctor.Create("EmulatedDevice", project)

    for dev in [dev11, dev12]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port1, RelationType("AffiliationPort"))
    for dev in [dev21, dev22, dev23]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port2, RelationType("AffiliationPort"))
    for dev in [dev31, dev32, dev33]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port3, RelationType("AffiliationPort"))

    eth11 = ctor.Create("EthIIIf", dev11)
    eth12 = ctor.Create("EthIIIf", dev12)
    eth21 = ctor.Create("EthIIIf", dev21)
    eth22 = ctor.Create("EthIIIf", dev22)
    eth23 = ctor.Create("EthIIIf", dev23)
    eth31 = ctor.Create("EthIIIf", dev31)
    eth32 = ctor.Create("EthIIIf", dev32)
    eth33 = ctor.Create("EthIIIf", dev33)

    for eth in [eth11, eth12, eth21, eth22, eth23, eth31, eth32, eth33]:
        eth.AddObject(eth_tag, RelationType("UserTag"))

    # Build the target_dict.  Skip eth32
    target_dict = {}
    target_dict[port1.GetObjectHandle()] = [eth11, eth12]
    target_dict[port2.GetObjectHandle()] = [eth21, eth22, eth23]
    target_dict[port3.GetObjectHandle()] = [eth31, eth33]

    # Set eth32 to some default
    eth32.Set("SourceMac", "55:55:55:55:55:55")

    # Test reset=True, target_step
    proc_func.handle_mac_range_update(
        target_dict,
        ["00:01:97:00:00:01"],
        ["00:00:00:00:01:00"],
        [0], [0],
        ["00:00:01:00:00:00"], True,
        "EthIIIf", "SourceMac")
    assert eth11.Get("SourceMac") == "00:01:97:00:00:01"
    assert eth12.Get("SourceMac") == "00:01:97:00:01:01"
    assert eth21.Get("SourceMac") == "00:01:98:00:00:01"
    assert eth22.Get("SourceMac") == "00:01:98:00:01:01"
    assert eth23.Get("SourceMac") == "00:01:98:00:02:01"
    assert eth31.Get("SourceMac") == "00:01:99:00:00:01"
    assert eth32.Get("SourceMac") == "55:55:55:55:55:55"
    assert eth33.Get("SourceMac") == "00:01:99:00:01:01"

    # Test reset=False, target_step
    proc_func.handle_mac_range_update(
        target_dict,
        ["00:01:97:00:00:01"],
        ["00:00:00:00:01:00"],
        [0], [0],
        ["00:00:01:00:00:00"], False,
        "EthIIIf", "SourceMac")
    assert eth11.Get("SourceMac") == "00:01:97:00:00:01"
    assert eth12.Get("SourceMac") == "00:01:97:00:01:01"
    assert eth21.Get("SourceMac") == "00:01:98:00:02:01"
    assert eth22.Get("SourceMac") == "00:01:98:00:03:01"
    assert eth23.Get("SourceMac") == "00:01:98:00:04:01"
    assert eth31.Get("SourceMac") == "00:01:99:00:05:01"
    assert eth32.Get("SourceMac") == "55:55:55:55:55:55"
    assert eth33.Get("SourceMac") == "00:01:99:00:06:01"

    # Test reset=True, target_step=0
    proc_func.handle_mac_range_update(
        target_dict,
        ["00:01:97:00:00:01"],
        ["00:00:00:00:01:00"],
        [0], [0],
        ["00:00:00:00:00:00"], True,
        "EthIIIf", "SourceMac")
    assert eth11.Get("SourceMac") == "00:01:97:00:00:01"
    assert eth12.Get("SourceMac") == "00:01:97:00:01:01"
    assert eth21.Get("SourceMac") == "00:01:97:00:00:01"
    assert eth22.Get("SourceMac") == "00:01:97:00:01:01"
    assert eth23.Get("SourceMac") == "00:01:97:00:02:01"
    assert eth31.Get("SourceMac") == "00:01:97:00:00:01"
    assert eth32.Get("SourceMac") == "55:55:55:55:55:55"
    assert eth33.Get("SourceMac") == "00:01:97:00:01:01"

    # Test reset=False, target_step=0 (original behavior)
    proc_func.handle_mac_range_update(
        target_dict,
        ["00:01:97:00:00:01"],
        ["00:00:00:00:01:00"],
        [0], [0],
        ["00:00:00:00:00:00"], False,
        "EthIIIf", "SourceMac")
    assert eth11.Get("SourceMac") == "00:01:97:00:00:01"
    assert eth12.Get("SourceMac") == "00:01:97:00:01:01"
    assert eth21.Get("SourceMac") == "00:01:97:00:02:01"
    assert eth22.Get("SourceMac") == "00:01:97:00:03:01"
    assert eth23.Get("SourceMac") == "00:01:97:00:04:01"
    assert eth31.Get("SourceMac") == "00:01:97:00:05:01"
    assert eth32.Get("SourceMac") == "55:55:55:55:55:55"
    assert eth33.Get("SourceMac") == "00:01:97:00:06:01"


def test_handle_mac_range_update_collection(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "Dev")
    tags.AddObject(tag, RelationType("UserTag"))
    eth_tag = ctor.Create("Tag", tags)
    eth_tag.Set("Name", "EthIIIf")
    tags.AddObject(tag, RelationType("UserTag"))

    port1 = ctor.Create("Port", project)
    dev11 = ctor.Create("EmulatedDevice", project)
    dev12 = ctor.Create("EmulatedDevice", project)
    port2 = ctor.Create("Port", project)
    dev21 = ctor.Create("EmulatedDevice", project)
    dev22 = ctor.Create("EmulatedDevice", project)
    dev23 = ctor.Create("EmulatedDevice", project)
    port3 = ctor.Create("Port", project)
    dev31 = ctor.Create("EmulatedDevice", project)
    dev32 = ctor.Create("EmulatedDevice", project)
    dev33 = ctor.Create("EmulatedDevice", project)

    for dev in [dev11, dev12]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port1, RelationType("AffiliationPort"))
    for dev in [dev21, dev22, dev23]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port2, RelationType("AffiliationPort"))
    for dev in [dev31, dev32, dev33]:
        dev.AddObject(tag, RelationType("UserTag"))
        dev.AddObject(port3, RelationType("AffiliationPort"))

    eth11 = ctor.Create("EthIIIf", dev11)
    eth12 = ctor.Create("EthIIIf", dev12)
    eth21 = ctor.Create("EthIIIf", dev21)
    eth22 = ctor.Create("EthIIIf", dev22)
    eth23 = ctor.Create("EthIIIf", dev23)
    eth31 = ctor.Create("EthIIIf", dev31)
    eth32 = ctor.Create("EthIIIf", dev32)
    eth33 = ctor.Create("EthIIIf", dev33)

    for eth in [eth11, eth12, eth21, eth22, eth23, eth31, eth32, eth33]:
        eth.AddObject(eth_tag, RelationType("UserTag"))

    # Build the target_dict.  Skip eth32
    target_dict = {}
    target_dict[port1.GetObjectHandle()] = [eth11, eth12]
    target_dict[port2.GetObjectHandle()] = [eth21, eth22, eth23]
    target_dict[port3.GetObjectHandle()] = [eth31, eth33]

    # Set eth32 to some default
    eth32.SetCollection("SrcMacList",
                        ["55:55:55:55:55:55", "55:55:55:55:55:54"])

    # Test reset=True, target_step
    proc_func.handle_mac_range_update(
        target_dict,
        ["00:01:97:00:00:01", "AA:BB:CC:00:00:01"],
        ["00:00:00:00:01:00", "00:00:00:01:00:00"],
        [0, 0], [0, 0],
        ["00:00:01:00:00:00", "00:01:00:00:00:00"], True,
        "EthIIIf", "SrcMacList")
    assert eth11.GetCollection("SrcMacList") == \
        ["00:01:97:00:00:01", "aa:bb:cc:00:00:01"]
    assert eth12.GetCollection("SrcMacList") == \
        ["00:01:97:00:01:01", "aa:bb:cc:01:00:01"]
    assert eth21.GetCollection("SrcMacList") == \
        ["00:01:98:00:00:01", "aa:bc:cc:00:00:01"]
    assert eth22.GetCollection("SrcMacList") == \
        ["00:01:98:00:01:01", "aa:bc:cc:01:00:01"]
    assert eth23.GetCollection("SrcMacList") == \
        ["00:01:98:00:02:01", "aa:bc:cc:02:00:01"]
    assert eth31.GetCollection("SrcMacList") == \
        ["00:01:99:00:00:01", "aa:bd:cc:00:00:01"]
    assert eth32.GetCollection("SrcMacList") == \
        ["55:55:55:55:55:55", "55:55:55:55:55:54"]
    assert eth33.GetCollection("SrcMacList") == \
        ["00:01:99:00:01:01", "aa:bd:cc:01:00:01"]

    # Test reset=False, target_step
    proc_func.handle_mac_range_update(
        target_dict,
        ["00:01:97:00:00:01", "AA:BB:CC:00:00:01"],
        ["00:00:00:00:01:00", "00:00:00:01:00:00"],
        [0, 0], [0, 0],
        ["00:00:01:00:00:00", "00:01:00:00:00:00"], False,
        "EthIIIf", "SrcMacList")
    assert eth11.GetCollection("SrcMacList") == \
        ["00:01:97:00:00:01", "aa:bb:cc:00:00:01"]
    assert eth12.GetCollection("SrcMacList") == \
        ["00:01:97:00:01:01", "aa:bb:cc:01:00:01"]
    assert eth21.GetCollection("SrcMacList") == \
        ["00:01:98:00:02:01", "aa:bc:cc:02:00:01"]
    assert eth22.GetCollection("SrcMacList") == \
        ["00:01:98:00:03:01", "aa:bc:cc:03:00:01"]
    assert eth23.GetCollection("SrcMacList") == \
        ["00:01:98:00:04:01", "aa:bc:cc:04:00:01"]
    assert eth31.GetCollection("SrcMacList") == \
        ["00:01:99:00:05:01", "aa:bd:cc:05:00:01"]
    assert eth32.GetCollection("SrcMacList") == \
        ["55:55:55:55:55:55", "55:55:55:55:55:54"]
    assert eth33.GetCollection("SrcMacList") == \
        ["00:01:99:00:06:01", "aa:bd:cc:06:00:01"]

    # Test reset=True, target_step=0
    proc_func.handle_mac_range_update(
        target_dict,
        ["00:01:97:00:00:01", "AA:BB:CC:00:00:01"],
        ["00:00:00:00:01:00", "00:00:00:01:00:00"],
        [0, 0], [0, 0],
        ["00:00:00:00:00:00", "00:00:00:00:00:00"], True,
        "EthIIIf", "SrcMacList")
    assert eth11.GetCollection("SrcMacList") == \
        ["00:01:97:00:00:01", "aa:bb:cc:00:00:01"]
    assert eth12.GetCollection("SrcMacList") == \
        ["00:01:97:00:01:01", "aa:bb:cc:01:00:01"]
    assert eth21.GetCollection("SrcMacList") == \
        ["00:01:97:00:00:01", "aa:bb:cc:00:00:01"]
    assert eth22.GetCollection("SrcMacList") == \
        ["00:01:97:00:01:01", "aa:bb:cc:01:00:01"]
    assert eth23.GetCollection("SrcMacList") == \
        ["00:01:97:00:02:01", "aa:bb:cc:02:00:01"]
    assert eth31.GetCollection("SrcMacList") == \
        ["00:01:97:00:00:01", "aa:bb:cc:00:00:01"]
    assert eth32.GetCollection("SrcMacList") == \
        ["55:55:55:55:55:55", "55:55:55:55:55:54"]
    assert eth33.GetCollection("SrcMacList") == \
        ["00:01:97:00:01:01", "aa:bb:cc:01:00:01"]

    # Test reset=False, target_step=0 (original behavior)
    proc_func.handle_mac_range_update(
        target_dict,
        ["00:01:97:00:00:01", "AA:BB:CC:00:00:01"],
        ["00:00:00:00:01:00", "00:00:00:01:00:00"],
        [0, 0], [0, 0],
        ["00:00:00:00:00:00", "00:00:00:00:00:00"], False,
        "EthIIIf", "SrcMacList")
    assert eth11.GetCollection("SrcMacList") == \
        ["00:01:97:00:00:01", "aa:bb:cc:00:00:01"]
    assert eth12.GetCollection("SrcMacList") == \
        ["00:01:97:00:01:01", "aa:bb:cc:01:00:01"]
    assert eth21.GetCollection("SrcMacList") == \
        ["00:01:97:00:02:01", "aa:bb:cc:02:00:01"]
    assert eth22.GetCollection("SrcMacList") == \
        ["00:01:97:00:03:01", "aa:bb:cc:03:00:01"]
    assert eth23.GetCollection("SrcMacList") == \
        ["00:01:97:00:04:01", "aa:bb:cc:04:00:01"]
    assert eth31.GetCollection("SrcMacList") == \
        ["00:01:97:00:05:01", "aa:bb:cc:05:00:01"]
    assert eth32.GetCollection("SrcMacList") == \
        ["55:55:55:55:55:55", "55:55:55:55:55:54"]
    assert eth33.GetCollection("SrcMacList") == \
        ["00:01:97:00:06:01", "aa:bb:cc:06:00:01"]


def test_apply_range_modifier_validation(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    tags = project.GetObject("Tags")
    assert tags
    ctor = CScriptableCreator()
    tmpl = ctor.Create("StmTemplateConfig", project)

    # Basic input checks
    res = proc_func.apply_range_modifier(None, None)
    assert "requires an StmTemplateConfig.  Received invalid element (None)." \
        in res
    res = proc_func.apply_range_modifier(project, None)
    assert "Received an object of type: project." in res
    res = proc_func.apply_range_modifier(tmpl, None)
    assert "requires an ElementTree modifier_ele (ModifierInfo)." in res

    # Missing TagName
    mod_ele_xml = "<StmPropertyModifier />"
    mod_ele = etree.fromstring(mod_ele_xml)
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "TagName attribute is required" in res

    # Missing ModifierInfo
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    mod_ele = etree.fromstring(mod_ele_xml)
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "ModifierInfo is required in the StmPropertyModifier:" in res

    # Invalid JSON ModifierInfo
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" " + \
        "ModifierInfo=\"Invalid Json String\" />"
    mod_ele = etree.fromstring(mod_ele_xml)
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "Invalid Json String is not valid JSON" in res

    # JSON ModifierInfo does not conform to schema
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" " + \
        "ModifierInfo=\"{}\" />"
    mod_ele = etree.fromstring(mod_ele_xml)
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "JSON object does not conform to given schema:" in res

    # ModifierInfo class does not exist
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = "500"
    pv_dict["step"] = "1"
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "InvalidNetworkIf"
    modifier_dict["propertyName"] = "IdList"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "Class InvalidNetworkIf does not exist" in res

    # ModifierInfo property does not exist on given class
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = "500"
    pv_dict["step"] = "1"
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "InvalidProperty"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "Property InvalidProperty does not exist on" in res

    # Missing a start value
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["step"] = "1"
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "ModifierInfo JSON is invalid or does not conform" in res

    # Missing a step
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = "1000"
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "ModifierInfo JSON is invalid or does not conform" in res

    # Invalid start value
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = "a"
    pv_dict["step"] = "1"
    pv_dict["targetObjectStep"] = "100"
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "Invalid value a in start" in res

    # Invalid start (list) value
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = ["1", "2", "a"]
    pv_dict["step"] = "1"
    pv_dict["targetObjectStep"] = "100"
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "IdList"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "Invalid value a in start" in res

    # Invalid step value
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = "1000"
    pv_dict["step"] = "a"
    pv_dict["targetObjectStep"] = "100"
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "Invalid value a in step" in res

    # Invalid step (list) value
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = ["1", "2", "3"]
    pv_dict["step"] = ["1", "abc"]
    pv_dict["targetObjectStep"] = "100"
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "IdList"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "Invalid value abc in step" in res

    # Invalid targetObjectStep value
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = "1000"
    pv_dict["step"] = "1"
    pv_dict["targetObjectStep"] = "invalid"
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "Invalid value invalid in targetObjectStep" in res

    # Invalid targetObjectStep (list) value
    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = ["1", "2", "3"]
    pv_dict["step"] = ["1"]
    pv_dict["targetObjectStep"] = ["100", "abc", "d"]
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "IdList"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "Invalid value abc in targetObjectStep" in res

    # Unsupported property type
    dev = ctor.Create("EmulatedDevice", project)
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "dev")
    tags.AddObject(tag, RelationType("UserTag"))
    dev.AddObject(tag, RelationType("UserTag"))
    tmpl.AddObject(dev, RelationType("GeneratedObject"))
    mod_ele_xml = "<StmPropertyModifier TagName=\"dev\" />"
    pv_dict = {}
    pv_dict["start"] = ["1", "2", "3"]
    pv_dict["step"] = ["1"]
    pv_dict["targetObjectStepList"] = ["100"]
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "EmulatedDevice"
    modifier_dict["propertyName"] = "Name"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert "string is not yet supported" in res


def test_apply_range_modifier_basic(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tmpl = ctor.Create("StmTemplateConfig", project)
    dev_list = []
    vlan_list = []
    qinq = None
    for i in range(0, 5):
        dev = ctor.Create("EmulatedDevice", project)
        vlan = ctor.Create("VlanIf", dev)
        dev_list.append(dev)
        vlan_list.append(vlan)
        if i == 3:
            qinq = ctor.Create("VlanIf", dev)
            qinq.AddObject(vlan, RelationType("StackedOnEndpoint"))

    for dev in dev_list:
        tmpl.AddObject(dev, RelationType("GeneratedObject"))

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "OuterVlan")
    tags.AddObject(tag, RelationType("UserTag"))
    # Skip 2nd one
    for idx, vlan in enumerate(vlan_list):
        if idx != 1:
            vlan.AddObject(tag, RelationType("UserTag"))

    mod_ele_xml = "<StmPropertyModifier TagName=\"OuterVlan\" />"
    pv_dict = {}
    pv_dict["start"] = "1324"
    pv_dict["step"] = "10"
    pv_dict["repeat"] = 1
    pv_dict["recycle"] = 3
    pv_dict["resetOnNewTargetObject"] = False
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))

    # Call the template processing function
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert res == ""

    # Check the VLAN IDs
    got_list = [vlan.Get("VlanId") for vlan in vlan_list]
    assert [1324, 100, 1324, 1334, 1334] == got_list
    assert qinq.Get("VlanId") == 100


def test_apply_range_modifier_list_specification_for_scalar(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tmpl = ctor.Create("StmTemplateConfig", project)
    dev_list = []
    vlan_list = []
    qinq = None
    for i in range(0, 5):
        dev = ctor.Create("EmulatedDevice", project)
        vlan = ctor.Create("VlanIf", dev)
        dev_list.append(dev)
        vlan_list.append(vlan)
        if i == 3:
            qinq = ctor.Create("VlanIf", dev)
            qinq.AddObject(vlan, RelationType("StackedOnEndpoint"))

    for dev in dev_list:
        tmpl.AddObject(dev, RelationType("GeneratedObject"))

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "OuterVlan")
    tags.AddObject(tag, RelationType("UserTag"))
    # Skip 2nd one
    for idx, vlan in enumerate(vlan_list):
        if idx != 1:
            vlan.AddObject(tag, RelationType("UserTag"))

    mod_ele_xml = "<StmPropertyModifier TagName=\"OuterVlan\" />"
    pv_dict = {}
    pv_dict["start"] = ["1325", "1324"]
    pv_dict["step"] = ["10", "20"]
    pv_dict["repeat"] = [1, 0]
    pv_dict["recycle"] = [3, 4]
    pv_dict["resetOnNewTargetObject"] = False
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))

    # Call the template processing function
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert res == ""

    # Check the VLAN IDs
    got_list = [vlan.Get("VlanId") for vlan in vlan_list]
    assert [1325, 100, 1325, 1335, 1335] == got_list
    assert qinq.Get("VlanId") == 100


def test_apply_range_modifier_to_collection(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    template = ctor.Create("StmTemplateConfig", project)
    dev_list = []
    net_block_list = []
    for i in range(0, 5):
        dev = ctor.Create("EmulatedDevice", project)
        bgp_proto = ctor.Create("BgpRouterConfig", dev)
        bgp_route = ctor.Create("BgpIpv4RouteConfig", bgp_proto)
        net_block = bgp_route.GetObject("Ipv4NetworkBlock")
        assert net_block is not None
        dev_list.append(dev)
        net_block_list.append(net_block)

    for dev in dev_list:
        template.AddObject(dev, RelationType("GeneratedObject"))

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "NetBlock")
    tags.AddObject(tag, RelationType("UserTag"))
    for net_block in net_block_list:
        net_block.AddObject(tag, RelationType("UserTag"))

    mod_ele_xml = "<StmPropertyModifier TagName=\"NetBlock\" />"
    pv_dict = {}
    pv_dict["start"] = ["131.0.0.0"]
    pv_dict["step"] = "0.1.0.0"
    pv_dict["repeat"] = 0
    pv_dict["recycle"] = 0
    pv_dict["resetOnNewTargetObject"] = False
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "Ipv4NetworkBlock"
    modifier_dict["propertyName"] = "StartIpList"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))

    # Call the template processing function
    res = proc_func.apply_range_modifier(template, mod_ele)
    assert res == ""

    # Check the Start IP Addresses
    assert net_block_list[0].GetCollection("StartIpList") == ["131.0.0.0"]
    assert net_block_list[1].GetCollection("StartIpList") == ["131.1.0.0"]
    assert net_block_list[2].GetCollection("StartIpList") == ["131.2.0.0"]
    assert net_block_list[3].GetCollection("StartIpList") == ["131.3.0.0"]
    assert net_block_list[4].GetCollection("StartIpList") == ["131.4.0.0"]


def test_apply_range_modifier_rollover(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tmpl_cfg = ctor.Create("StmTemplateConfig", project)
    dev_list = []
    vlan_list = []
    for i in range(0, 5):
        dev = ctor.Create("EmulatedDevice", project)
        vlan = ctor.Create("VlanIf", dev)
        dev_list.append(dev)
        vlan_list.append(vlan)

    for dev in dev_list:
        tmpl_cfg.AddObject(dev, RelationType("GeneratedObject"))

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "OuterVlan")
    tags.AddObject(tag, RelationType("UserTag"))
    # Skip 2nd one
    for idx, vlan in enumerate(vlan_list):
        if idx != 1:
            vlan.AddObject(tag, RelationType("UserTag"))

    mod_ele_xml = "<StmPropertyModifier TagName=\"OuterVlan\" />"
    pv_dict = {}
    pv_dict["start"] = ["4091"]
    pv_dict["step"] = "3"
    pv_dict["repeat"] = 0
    pv_dict["recycle"] = 4
    pv_dict["resetOnNewTargetObject"] = False
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))

    # Call the template processing function
    res = proc_func.apply_range_modifier(tmpl_cfg, mod_ele)
    assert res == ""

    # Check the VLAN IDs
    got_list = [vlan.Get("VlanId") for vlan in vlan_list]
    assert [4091, 100, 4094, 1, 4] == got_list


def test_apply_range_modifier_multiple_tags(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tmpl_cfg = ctor.Create("StmTemplateConfig", project)
    dev_list = []
    vlan_list = []
    for i in range(0, 5):
        dev = ctor.Create("EmulatedDevice", project)
        vlan = ctor.Create("VlanIf", dev)
        dev_list.append(dev)
        vlan_list.append(vlan)

    for dev in dev_list:
        tmpl_cfg.AddObject(dev, RelationType("GeneratedObject"))

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    fake_tag = ctor.Create("Tag", tags)
    fake_tag.Set("Name", "FakeTag")
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "OuterVlan")

    tags.AddObject(tag, RelationType("UserTag"))
    tags.AddObject(fake_tag, RelationType("UserTag"))

    for idx, vlan in enumerate(vlan_list):
        vlan.AddObject(fake_tag, RelationType("UserTag"))
        vlan.AddObject(tag, RelationType("UserTag"))

    mod_ele_xml = "<StmPropertyModifier TagName=\"OuterVlan\" />"
    pv_dict = {}
    pv_dict["start"] = ["10"]
    pv_dict["step"] = "3"
    pv_dict["repeat"] = 0
    pv_dict["recycle"] = 0
    pv_dict["resetOnNewTargetObject"] = False
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))

    # Call the template processing function
    res = proc_func.apply_range_modifier(tmpl_cfg, mod_ele)
    assert res == ""

    # Check the VLAN IDs
    got_list = [vlan.Get("VlanId") for vlan in vlan_list]
    assert [10, 13, 16, 19, 22] == got_list


def test_apply_range_modifier_reset_on_new_target(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "ttVlanIf")
    tags.AddObject(tag, RelationType("UserTag"))

    # This is not a very orthodox way of using this feature
    # but it tests the case where counts are reset when the
    # target object changes.
    tmpl = ctor.Create("StmTemplateConfig", project)
    dev1 = ctor.Create("EmulatedDevice", project)
    vlan11 = ctor.Create("VlanIf", dev1)
    vlan12 = ctor.Create("VlanIf", dev1)
    vlan13 = ctor.Create("VlanIf", dev1)
    dev2 = ctor.Create("EmulatedDevice", project)
    vlan21 = ctor.Create("VlanIf", dev2)
    vlan22 = ctor.Create("Vlanif", dev2)
    dev3 = ctor.Create("EmulatedDevice", project)
    vlan31 = ctor.Create("VlanIf", dev3)
    vlan32 = ctor.Create("VlanIf", dev3)
    vlan33 = ctor.Create("VlanIf", dev3)
    vlan_list = [vlan11, vlan12, vlan13, vlan21, vlan22, vlan31,
                 vlan32, vlan33]
    for vlan in vlan_list:
        tmpl.AddObject(vlan, RelationType("GeneratedObject"))
        vlan.AddObject(tag, RelationType("UserTag"))

    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = ["100"]
    pv_dict["step"] = "3"
    pv_dict["repeat"] = 0
    pv_dict["recycle"] = 0
    pv_dict["targetObjectStep"] = "100"
    pv_dict["resetOnNewTargetObject"] = True
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "VlanId"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))

    # Call the template processing function
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert res == ""

    # Check the VLAN IDs
    assert vlan11.Get("VlanId") == 100
    assert vlan12.Get("VlanId") == 103
    assert vlan13.Get("VlanId") == 106
    assert vlan21.Get("VlanId") == 200
    assert vlan22.Get("VlanId") == 203
    assert vlan31.Get("VlanId") == 300
    assert vlan32.Get("VlanId") == 303
    assert vlan33.Get("VlanId") == 306


def test_apply_range_modifier_list_reset_on_new_target(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "ttVlanIf")
    tags.AddObject(tag, RelationType("UserTag"))

    # This is not a very orthodox way of using this feature
    # but it tests the case where counts are reset when the
    # target object changes.
    tmpl = ctor.Create("StmTemplateConfig", project)
    dev1 = ctor.Create("EmulatedDevice", project)
    vlan11 = ctor.Create("VlanIf", dev1)
    vlan12 = ctor.Create("VlanIf", dev1)
    vlan13 = ctor.Create("VlanIf", dev1)
    dev2 = ctor.Create("EmulatedDevice", project)
    vlan21 = ctor.Create("VlanIf", dev2)
    vlan22 = ctor.Create("Vlanif", dev2)
    dev3 = ctor.Create("EmulatedDevice", project)
    vlan31 = ctor.Create("VlanIf", dev3)
    vlan32 = ctor.Create("VlanIf", dev3)
    vlan33 = ctor.Create("VlanIf", dev3)
    vlan_list = [vlan11, vlan12, vlan13, vlan21, vlan22, vlan31,
                 vlan32, vlan33]
    for vlan in vlan_list:
        tmpl.AddObject(vlan, RelationType("GeneratedObject"))
        vlan.AddObject(tag, RelationType("UserTag"))

    mod_ele_xml = "<StmPropertyModifier TagName=\"ttVlanIf\" />"
    pv_dict = {}
    pv_dict["start"] = ["100", "200", "1024", "3", "10"]
    pv_dict["step"] = ["3", "50", "2", "1"]
    pv_dict["repeat"] = [0, 0, 1, 0, 1]
    pv_dict["recycle"] = [0, 2, 0]
    pv_dict["targetObjectStep"] = ["100", "200", "0", "0", "1000"]
    pv_dict["resetOnNewTargetObject"] = True
    modifier_dict = {}
    modifier_dict["modifierType"] = "RANGE"
    modifier_dict["objectName"] = "VlanIf"
    modifier_dict["propertyName"] = "IdList"
    modifier_dict["propertyValueDict"] = pv_dict
    mod_ele = etree.fromstring(mod_ele_xml)
    mod_ele.set("ModifierInfo", json.dumps(modifier_dict))

    # Call the template processing function
    res = proc_func.apply_range_modifier(tmpl, mod_ele)
    assert res == ""

    # Check the VLAN IDs
    assert vlan11.GetCollection("IdList") == [100, 200, 1024, 3, 10]
    assert vlan12.GetCollection("IdList") == [103, 250, 1024, 4, 10]
    assert vlan13.GetCollection("IdList") == [106, 200, 1026, 5, 13]
    assert vlan21.GetCollection("IdList") == [200, 400, 1024, 3, 1010]
    assert vlan22.GetCollection("IdList") == [203, 450, 1024, 4, 1010]
    assert vlan31.GetCollection("IdList") == [300, 600, 1024, 3, 2010]
    assert vlan32.GetCollection("IdList") == [303, 650, 1024, 4, 2010]
    assert vlan33.GetCollection("IdList") == [306, 600, 1026, 5, 2013]


def test_get_zero_value():
    for var_type in ["u8", "u16", "u32", "u64"]:
        err_str, val = proc_func.get_zero_value(var_type)
        assert err_str == ""
        assert val == 0
    err_str, val = proc_func.get_zero_value("ip")
    assert err_str == ""
    assert val == "0.0.0.0"
    err_str, val = proc_func.get_zero_value("ipv6")
    assert err_str == ""
    assert val == "0::0"
    err_str, val = proc_func.get_zero_value("mac")
    assert err_str == ""
    assert val == "00:00:00:00:00:00"
    err_str, val = proc_func.get_zero_value("invalidType")
    assert "Unsupported property type: invalidType." in err_str
    assert val == 0


def test_check_value_type():
    # u8
    assert proc_func.check_value_type("u8", 21) == ""
    assert proc_func.check_value_type("u8", "21") == ""
    assert proc_func.check_value_type("u8", 0) == ""
    assert proc_func.check_value_type("u8", 255) == ""
    for val in [-1, 257, "a"]:
        assert "is invalid" in proc_func.check_value_type("u8", val)
    # u16
    assert proc_func.check_value_type("u16", 22) == ""
    assert proc_func.check_value_type("u16", "22") == ""
    assert proc_func.check_value_type("u16", 0) == ""
    assert proc_func.check_value_type("u16", pow(2, 16) - 1) == ""
    for val in [-1, pow(2, 16), "a"]:
        assert "is invalid" in proc_func.check_value_type("u16", val)
    # u32
    assert proc_func.check_value_type("u32", 23) == ""
    assert proc_func.check_value_type("u32", "23") == ""
    assert proc_func.check_value_type("u32", 0) == ""
    assert proc_func.check_value_type("u32", pow(2, 32) - 1) == ""
    for val in [-1, pow(2, 32), "a"]:
        assert "is invalid" in proc_func.check_value_type("u32", val)
    # u64
    assert proc_func.check_value_type("u64", 22) == ""
    assert proc_func.check_value_type("u64", "22") == ""
    assert proc_func.check_value_type("u64", 0) == ""
    assert proc_func.check_value_type("u64", pow(2, 64) - 1) == ""
    for val in [-1, pow(2, 64), "a"]:
        assert "is invalid" in proc_func.check_value_type("u64", val)
    # ip
    assert proc_func.check_value_type("ip", "0.0.0.0") == ""
    assert proc_func.check_value_type("ip", "1.2.3.4") == ""
    assert proc_func.check_value_type("ip", "255.255.255.255") == ""
    for val in ["F.F.F.F", "00:00:00:00:00:00", "invalidValue"]:
        assert "is invalid" in proc_func.check_value_type("ip", val)
    # ipv6
    assert proc_func.check_value_type("ipv6", "0::0") == ""
    assert proc_func.check_value_type("ipv6", "::0") == ""
    assert proc_func.check_value_type("ipv6", "::") == ""
    assert proc_func.check_value_type(
        "ipv6", "2001:1:2:3::F:ABCD") == ""
    assert proc_func.check_value_type(
        "ipv6", "FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF") == ""
    for val in ["1.2.3.4", "0:0:0:0:1:0:0:0:0", "invalidValue"]:
        assert "is invalid" in proc_func.check_value_type("ipv6", val)
    # mac
    assert proc_func.check_value_type("mac", "00:00:00:00:00:00") == ""
    assert proc_func.check_value_type("mac", "0:0:0:0:0:0") == ""
    assert proc_func.check_value_type("mac", "A:B:C:D:E:F") == ""
    assert proc_func.check_value_type("mac", "FF:FF:FF:FF:FF:FF") == ""
    for val in ["1.2.3.4", "A:B:C:D:E:F:1:2:3", "invalidValue"]:
        assert "is invalid" in proc_func.check_value_type("mac", val)
