from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import spirent.methodology.utils.xml_config_utils as xml_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


# This command modifies properties (element's attribute values) in the
# XML template.  TagNameList specifies a list of tags to filter elements
# in the tree on.  If it is unspecified, all elements that can be modified
# will be.  If it is specified, even if some of the tags don't refer to
# any elements, it will be used for filtering.  PropertyValueList can
# contain a mixture of Object.Property=Value strings.  Different kinds of
# objects can be configured at the same time though if the TagNameList is
# used, all objects to be configured must be represented in the TagNameList.
# If a specified object is not modified because it is not contained in the
# TagNameList, an error will be returned. Tag names that don't point to
# any objects will not error out, only a warning will be logged.
def validate(StmTemplateConfig, TagNameList,
             PropertyList, ValueList):
    return ""


def run(StmTemplateConfig, TagNameList,
        PropertyList, ValueList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("Run ModifyTemplatePropertyCommand")

    hnd_reg = CHandleRegistry.Instance()
    template = hnd_reg.Find(StmTemplateConfig)
    if template is None:
        plLogger.LogError("Invalid or missing StmTemplateConfig")
    if not template.IsTypeOf("StmTemplateConfig"):
        plLogger.LogError("Input StmTemplateConfig is not an " +
                          "StmTemplateConfig")
        return False

    # Parse the PropertyList and ValueList
    attr_dict, msg = xml_utils.parse_prop_and_val_list(PropertyList,
                                                       ValueList)
    if msg != "":
        plLogger.LogError("Failed to parse PropertyList and " +
                          "ValueList: " + msg)
        return False

    plLogger.LogDebug("attr_dict contains: " + str(attr_dict))
    root = etree.fromstring(template.Get("TemplateXml"))

    # Build a unique list of the tagged objects and print a warning if no
    # objects found
    tagged_objs = set()
    for tagName in TagNameList:
        taggedObjects = xml_utils.find_tagged_elements_by_tag_name(root,
                                                                   [tagName])
        # Check if returned list is empty
        if not taggedObjects:
            plLogger.LogWarn("No tagged objects found for tag: " + str(tagName))
        else:
            for tagged_obj in taggedObjects:
                if tagged_obj.tag != "Tags":
                    tagged_objs.add(tagged_obj)

    for tagged_obj in tagged_objs:
        plLogger.LogDebug("tagged_obj: " + str(tagged_obj))

    for obj_type in attr_dict["obj_list"]:
        if len(TagNameList) > 0:
            # If there are tags specified (valid or invalid)
            found = False
            for tagged_obj in tagged_objs:
                # Go through list of tagged objects and determine if
                # the object type matches a tagged object
                if obj_type == tagged_obj.tag:
                    # If it matches, set all given properties for that object
                    found = True
                    for param in attr_dict[tagged_obj.tag]:
                        tagged_obj.set(param, attr_dict[tagged_obj.tag + "." + param])
            if not found:
                # Object to modify was not found in list of tagged objects
                err = "Did not find object " + obj_type + " in list of " + \
                      "tagged objects. The following properties in " + \
                      obj_type + " were not modified: " + str(attr_dict[obj_type])
                plLogger.LogError(err)
                raise RuntimeError(err)
        else:
            # Else no tags specified, modify everything
            ele_list = root.findall(".//" + obj_type)
            plLogger.LogDebug("ele_list contains: " + str(ele_list))
            for ele in ele_list:
                for param in attr_dict[ele.tag]:
                    ele.set(param, attr_dict[ele.tag + "." + param])

    template.Set("TemplateXml", etree.tostring(root))
    plLogger.LogDebug("new TemplateXml is " + template.Get("TemplateXml"))
    return True


def reset():
    return True
