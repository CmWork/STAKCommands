from StcIntPythonPL import *
import xml.etree.ElementTree as ET
import re
import os


def validate(FileName):

    if not os.path.isfile(FileName):
        return 'File not found. Abort validation...'

    return ''


def run(FileName):

    if not parseConfigTree(FileName):
        return False

    return True


def parseConfigTree(FileName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.parseConfigTree.ValidateTestCompatibleCommand")

    tree = ET.parse(FileName)
    root = tree.getroot()

    sequencer = root.find("Sequencer")

    if sequencer is None:
        plLogger.LogError("Can't find sequencer")
        return False

    stc_classes = CMeta.GetClasses()

    for child in sequencer.getchildren():
        if re.search('[cC]ommand$', child.tag) is not None:
            if child.tag not in stc_classes:
                plLogger.LogError("Unknown command: " + child.tag + " is detected")
                return False

    plLogger.LogDebug("end.parseConfigTree.ValidateTestCompatibleCommand")
    return True


def reset(FileName):

    return True