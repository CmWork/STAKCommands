def get_subnet_tag_prefix(subnet):
    subnet_id = str(subnet["id"])
    subnet_name = str(subnet["name"])
    return subnet_name + "_" + subnet_id + "_"


def get_dev_tag(subnet):
    return "ttEmulatedDevice"


def get_ipv4If_tag(subnet):
    return "ttIpv4If"


def get_ethIIIf_tag(subnet):
    return "ttEthIIIf"


def get_dhcpv4_tag(subnet):
    return "ttDhcpv4BlockConfig"
