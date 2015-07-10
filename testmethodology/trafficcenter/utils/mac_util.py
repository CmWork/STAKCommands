from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import tag_name_util
from spirent.methodology.utils import tag_utils


def detect_source_mac(port_list):
    with AutoCommand("DetectSourceMacCommand") as detect_cmd:
        detect_cmd.SetCollection("PortList", port_list)
        detect_cmd.Execute()


def get_ethii_ifs(subnet):
    tag_prefix = tag_name_util.get_subnet_tag_prefix(subnet)
    tag_name = tag_prefix + tag_name_util.get_ethIIIf_tag(subnet)
    ethii_ifs = tag_utils.get_tagged_objects_from_string_names(
        [tag_name]
        )
    return ethii_ifs


def randomize_source_mac(subnet):
    ctor = CScriptableCreator()
    ethii_ifs = get_ethii_ifs(subnet)
    for ethii_if in ethii_ifs:
        ctor.Create('Rfc4814EthIIIfDecorator', ethii_if)
