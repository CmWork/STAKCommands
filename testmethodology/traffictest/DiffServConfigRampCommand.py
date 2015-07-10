from StcIntPythonPL import *


PKG = "spirent.methodology"
OBJ_KEY = 'spirent.methodology.DiffServ_CfgRamp'


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StreamTagNameList, ExpPktLossCount, ExpMaxJitter, ExpMaxLatency,
             ExpMaxOopCount, ExpMaxLatePktCount, ExpMaxDupPktCount):
    return ''


def run(StreamTagNameList, ExpPktLossCount, ExpMaxJitter, ExpMaxLatency,
        ExpMaxOopCount, ExpMaxLatePktCount, ExpMaxDupPktCount):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("Running DiffServCfgRampCommand...")

    for tag in StreamTagNameList:
        info = [(tag, 'exp_pktloss', ExpPktLossCount),
                (tag, 'exp_maxjitter', ExpMaxJitter),
                (tag, 'exp_maxlatency', ExpMaxLatency),
                (tag, 'exp_maxoop', ExpMaxOopCount),
                (tag, 'exp_maxlatepkt', ExpMaxLatePktCount),
                (tag, 'exp_maxduppkt', ExpMaxDupPktCount)]

        dict = {}
        if not CObjectRefStore.Exists(OBJ_KEY):
            for sb, param, data in info:
                dict.setdefault(sb, {})[param] = data
            CObjectRefStore.Put(OBJ_KEY, dict)
        else:
            dict = CObjectRefStore.Get(OBJ_KEY)
            for sb, param, data in info:
                dict.setdefault(sb, {})[param] = data

    dict = CObjectRefStore.Get(OBJ_KEY)
    plLogger.LogDebug("   dict: " + str(dict))
    return True


def reset():
    return True
