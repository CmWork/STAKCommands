from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import utils.data_model_utils as dm_utils
import utils.xml_config_utils as xml_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateConfig, SrcTagName, TargetTagName, RelationName,
             RemoveRelation):
    # FIXME:
    # Check that RelationName is a real relation type

    return ""


def run(StmTemplateConfig, SrcTagName, TargetTagName, RelationName,
        RemoveRelation):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("run ConfigTemplateRelationCommand")
    # Before walking the tree, make sure the relation is a valid one
    try:
        RelationType(RelationName)
    except RuntimeError as e:
        # Invalid name
        if 'does not exist' in str(e):
            err = "Relation name " + RelationName + \
                  " is not a valid relation type"
            plLogger.LogError(err)
            raise RuntimeError(err)
        else:
            raise e
    hnd_reg = CHandleRegistry.Instance()
    template = hnd_reg.Find(StmTemplateConfig)
    if not template.IsTypeOf("StmTemplateConfig"):
        plLogger.LogError("Input StmTemplateConfig is not " +
                          "an StmTemplateConfig")
        return False

    xml_str = template.Get("TemplateXml")
    root = etree.fromstring(xml_str)

    # Find the tag IDs
    source_tag_ele = xml_utils.find_tag_elements(root, SrcTagName)
    if not source_tag_ele:
        plLogger.LogError("Could not find a " + SrcTagName +
                          " in the template XML")
        return False
    source_tag_id = source_tag_ele[0].get("id")
    plLogger.LogDebug("source_tag_id: " + str(source_tag_id))
    target_tag_ele = xml_utils.find_tag_elements(root, TargetTagName)
    if not target_tag_ele:
        plLogger.LogError("Could not find a " + TargetTagName +
                          " in the template XML")
        return False
    target_tag_id = target_tag_ele[0].get("id")
    plLogger.LogDebug("target_tag_id: " + str(target_tag_id))

    # Find the tagged objects
    source_ele_list = xml_utils.find_tagged_elements(root, source_tag_id)
    if len(source_ele_list) == 0:
        plLogger.LogError("Could not find a element tagged with " +
                          SrcTagName + " in the template XML")
        return False
    for source_ele in source_ele_list:
        source_tag = source_ele.tag
        if source_tag == "Tags":
            # Skip the Tags element
            continue
        plLogger.LogDebug("source_ele_id: " + str(source_ele.get("id")))
        target_ele_list = xml_utils.find_tagged_elements(root, target_tag_id)

        if len(target_ele_list) == 0:
            plLogger.LogError("Could not find an element tagged " +
                              "with " + TargetTagName + " in the template XML")
            return False
        for target_ele in target_ele_list:
            target_tag = target_ele.tag
            if target_tag == "Tags":
                # Skip the Tags element
                continue
            target_id = target_ele.get("id")
            plLogger.LogDebug("target_id: " + str(target_id))

            if RemoveRelation:
                # Remove the existing relation between source and target
                plLogger.LogDebug("Removing a relation...")
                for child in source_ele:
                    plLogger.LogDebug("child: " + child.tag)
                    if child.tag == "Relation":
                        plLogger.LogDebug("type: " + child.get("type"))
                        plLogger.LogDebug("target: " + child.get("target"))
                        if child.get("type") == RelationName and \
                           child.get("target") == str(target_id):
                            source_ele.remove(child)
            else:
                plLogger.LogDebug(" adding a relation...")
                # Validate relations given the source and target
                if not dm_utils.validate_class_relation(source_tag,
                                                        target_tag,
                                                        RelationName):
                    err = "Relation name " + RelationName + \
                          " is not valid between " + source_tag + \
                          " and " + target_tag + " objects"
                    plLogger.LogError(err)
                    raise RuntimeError(err)
                # Build the relation from source to target
                xml_utils.create_relation_element(source_ele,
                                                  RelationName,
                                                  target_id)
    plLogger.LogDebug("new xml: " + etree.tostring(root))
    template.Set("TemplateXml", etree.tostring(root))

    return True


def reset():
    return True
