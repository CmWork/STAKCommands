from StcIntPythonPL import *
import sys
import os
import xml.etree.ElementTree as etree
from utils.txml_utils import MetaManager as meta_mgr
from utils.methodologymanagerConst import MethodologyManagerConst as mgr_const


def validate(StmTestCase):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("begin.validate.GetFeatureIdsFromTestCommand")

    if StmTestCase is None:
        plLogger.LogError("Invalid test case provided as input")
        return "ERROR: Invalid test case provided as input."

    # Check that the test case exists
    hnd_reg = CHandleRegistry.Instance()
    test_case = hnd_reg.Find(StmTestCase)
    if test_case is None:
        plLogger.LogError("Unable to find StmTestCase with handle " +
                          str(StmTestCase) + " in the system.")
        return "ERROR: Could not find StmTestCase."

    txml_path = test_case.Get("Path")
    plLogger.LogDebug("txml_path: " + str(txml_path))

    plLogger.LogDebug("end.validate.GetFeatureIdsFromTestCommand")
    return ""


def run(StmTestCase):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.GetFeatureIdsFromTestCommand")
    hnd_reg = CHandleRegistry.Instance()

    test_case = hnd_reg.Find(StmTestCase)
    if test_case is None:
        plLogger.LogError("Was unable to find StmTestCase with handle " +
                          str(StmTestCase) + " in the system.")
        return False

    txml_path = os.path.join(test_case.Get("Path"), mgr_const.MM_META_FILE_NAME)

    root = None
    try:
        element_tree = etree.parse(os.path.abspath(txml_path))
        if element_tree is not None:
            root = element_tree.getroot()
    except:
        plLogger.LogError("Exception encountered parsing TXML file: " + str(sys.exc_info()[0]))
        plLogger.LogError("More exception info: " + str(sys.exc_info()[1]))
        return False

    if root is None:
        plLogger.LogError("Could not parse TXML")
        return False

    featureIds = []
    for feature_tag in root.findall(".//" + meta_mgr.TI_FEATURE):
        plLogger.LogDebug("Found feature_tag: " + str(feature_tag))
        featureIds.append(feature_tag.get(meta_mgr.TI_ID))
    plLogger.LogDebug("featureIds: " + str(featureIds))
    this_cmd = hnd_reg.Find(__commandHandle__)
    this_cmd.SetCollection("FeatureIdList", featureIds)

    plLogger.LogDebug("end.run.GetFeatureIdsFromTestCommand")
    return True


def reset():
    return True
