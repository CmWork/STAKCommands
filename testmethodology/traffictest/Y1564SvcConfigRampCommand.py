from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


PKG = "spirent.methodology"


OBJ_KEY = 'spirent.methodology.Y1564_SvcCfgRamp'


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(CommandTagName, IterationDuration, StartBw, CirBw, EirBw,
             OvershootBw, StepCount, ExpPktLossCount, ExpRfc4689AvgJitter,
             ExpMaxJitter, ExpAvgLatency, ExpMaxLatency, ExpMaxOopCount,
             ExpMaxLatePktCount):
    return ''


def run(CommandTagName, IterationDuration, StartBw, CirBw, EirBw, OvershootBw,
        StepCount, ExpPktLossCount, ExpRfc4689AvgJitter, ExpMaxJitter,
        ExpAvgLatency, ExpMaxLatency, ExpMaxOopCount, ExpMaxLatePktCount):
    cmd_dict = {
        'start_bw': StartBw,
        'cir_bw': CirBw,
        'eir_bw': EirBw,
        'ovr_bw': OvershootBw,
        'step_bw': StepCount,
        'exp_pktloss': ExpPktLossCount,
        'exp_avgjitter': ExpRfc4689AvgJitter,
        'exp_maxjitter': ExpMaxJitter,
        'exp_avglatency': ExpAvgLatency,
        'exp_maxlatency': ExpMaxLatency,
        'exp_maxoop': ExpMaxOopCount,
        'exp_maxlatepkt': ExpMaxLatePktCount}
    # Additional work to chain/configure other properties needed
    CObjectRefStore.Put(OBJ_KEY, cmd_dict, True)
    cmd_list = \
        tag_utils.get_tagged_objects_from_string_names([CommandTagName])
    for cmd in cmd_list:
        # Assume only certain commands are tagged
        if cmd.IsTypeOf('WaitCommand'):
            cmd.Set('WaitTime', float(IterationDuration))
        elif cmd.IsTypeOf(PKG + '.ObjectIteratorCommand'):
            bw_list = []
            if StartBw < CirBw:
                stepBw = (CirBw - StartBw) / StepCount
                if stepBw == 0:
                    bw_list.append(StartBw)
                else:
                    bw = StartBw
                    while (bw <= CirBw):
                        if CirBw - bw < stepBw:
                            bw = CirBw
                        bw_list.append(bw)
                        bw = bw + stepBw
            else:
                bw_list.append(CirBw)
            bw_list.append(CirBw + EirBw)
            bw_list.append(CirBw + EirBw + OvershootBw)
            cmd.SetCollection('ValueList', [str(x) for x in bw_list])
    return True


def reset():
    return True
