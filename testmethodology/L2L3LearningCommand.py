from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.data_model_utils as dm_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(ObjectList, TagNameList, EnableL2Learning, EnableL3Learning,
             L2LearningOption, WaitForArpToFinish, ForceArp, VerifyArp):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate L2L3LearningCommand")

    return ""


def run(ObjectList, TagNameList, EnableL2Learning, EnableL3Learning,
        L2LearningOption, WaitForArpToFinish, ForceArp, VerifyArp):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run L2L3LearningCommand")
    this_cmd = get_this_cmd()

    # Log that if neither L2 or L3 is enabled, the command will be return
    if not EnableL2Learning and not EnableL3Learning:
        plLogger.LogInfo("Both L2 and L3 Learning not enabled, \
                          skipping L2L3LearningCommand")
        return True

    l2_handle_list = []
    l3_handle_list = []

    # Handle and Tag validation
    if len(ObjectList) == 0 and len(TagNameList) == 0:
        # If both ObjectList and TagNameList empty, project will be used as default
        plLogger.LogInfo("ObjectList and TagNameList empty, project will be used as default")
    else:
        # If invalid handle type given, command should error
        err = validate_handle_types(ObjectList, EnableL2Learning, EnableL3Learning)
        if err != "":
            this_cmd.Set('Status', err)
            return False

        l2_handle_list, l3_handle_list = get_valid_handles(ObjectList, TagNameList)
        if EnableL2Learning and not EnableL3Learning:
            if len(l2_handle_list) == 0:
                plLogger.LogWarn("WARNING: Tagged objects not valid for L2Learning."
                                 "Skipping learning command")
                return True
        elif not EnableL2Learning and EnableL3Learning:
            if len(l3_handle_list) == 0:
                plLogger.LogWarn("WARNING: Tagged objects not valid for L3Learning."
                                 "Skipping learning command")
                return True
        elif EnableL2Learning and EnableL3Learning:
            if len(l2_handle_list) == 0 and len(l3_handle_list) == 0:
                plLogger.LogWarn("WARNING: Tagged objects not valid for L2L3Learning."
                                 "Skipping learning command")
                return True
            elif len(l2_handle_list) == 0 and len(l3_handle_list) != 0:
                plLogger.LogInfo("Tagged objects not valid for L2Learning."
                                 "Skipping L2 learning command")
                EnableL2Learning = False

    # Call BLL commands
    if EnableL2Learning:
        l2StartCmd = l2_learning_start(l2_handle_list, L2LearningOption)
        if l2StartCmd.Get('State') != 'COMPLETED':
            this_cmd.Set('Status', "L2LearningStartCommand did not pass: " +
                         l2StartCmd.Get('Status'))
            l2StartCmd.MarkDelete()
            return False
        l2StartCmd.MarkDelete()

        l2StopCmd = l2_learning_stop(l2_handle_list)
        if l2StopCmd.Get('State') != 'COMPLETED':
            this_cmd.Set('Status', "L2LearningStopCommand did not pass: " +
                         l2StopCmd.Get('Status'))
            l2StopCmd.MarkDelete()
            return False
        l2StopCmd.MarkDelete()

    if EnableL3Learning:
        l3StartCmd = l3_learning_start(l3_handle_list, WaitForArpToFinish, ForceArp)
        if l3StartCmd.Get('State') != 'COMPLETED':
            this_cmd.Set('Status', "ArpNdStartCommand did not pass: " +
                         l3StartCmd.Get('Status'))
            l3StartCmd.MarkDelete()
            return False
        l3StartCmd.MarkDelete()

        l3StopCmd = l3_learning_stop(l3_handle_list)
        if l3StopCmd.Get('State') != 'COMPLETED':
            this_cmd.Set('Status', "ArpNdStopCommand did not pass: " +
                         l3StopCmd.Get('Status'))
            l3StopCmd.MarkDelete()
            return False
        l3StopCmd.MarkDelete()

        if VerifyArp:
            verifyCmd = verify_arp(l3_handle_list)
            if not (verifyCmd.Get('State') == 'COMPLETED' and
               verifyCmd.Get('PassFailState') == 'PASSED'):
                this_cmd.Set('Status', "ArpNdVerifyResolvedCommand did not pass: " +
                             verifyCmd.Get('Status'))
                this_cmd.Set('PassFailState', 'FAILED')
                verifyCmd.MarkDelete()
                return False
            verifyCmd.MarkDelete()

    return True


def l2_learning_start(handle_list, learning_option):
    ctor = CScriptableCreator()
    l2_start_cmd = ctor.CreateCommand("L2LearningStartCommand")
    l2_start_cmd.SetCollection("HandleList", handle_list)
    l2_start_cmd.Set("L2LearningOption", learning_option)
    l2_start_cmd.Execute()
    return l2_start_cmd


def l2_learning_stop(handle_list):
    ctor = CScriptableCreator()
    l2_stop_cmd = ctor.CreateCommand("L2LearningStopCommand")
    l2_stop_cmd.SetCollection("HandleList", handle_list)
    l2_stop_cmd.Execute()
    return l2_stop_cmd


def l3_learning_start(handle_list, wait_for_arp, force_arp):
    ctor = CScriptableCreator()
    l3_start_cmd = ctor.CreateCommand("ArpNdStartCommand")
    l3_start_cmd.SetCollection("HandleList", handle_list)
    l3_start_cmd.Set("WaitForArpToFinish", wait_for_arp)
    l3_start_cmd.Set("ForceArp", force_arp)
    l3_start_cmd.Execute()
    return l3_start_cmd


def l3_learning_stop(handle_list):
    ctor = CScriptableCreator()
    l3_stop_cmd = ctor.CreateCommand("ArpNdStopCommand")
    l3_stop_cmd.SetCollection("HandleList", handle_list)
    l3_stop_cmd.Execute()
    return l3_stop_cmd


def verify_arp(handle_list):
    ctor = CScriptableCreator()
    verify_cmd = ctor.CreateCommand("ArpNdVerifyResolvedCommand")
    verify_cmd.SetCollection("HandleList", handle_list)
    verify_cmd.Execute()
    return verify_cmd


def validate_handle_types(handle_list, enable_l2, enable_l3):
    hnd_reg = CHandleRegistry.Instance()
    # The L2 learning command only allows handles of type Port and StreamBlock
    if enable_l2 and not enable_l3:
        for hnd in handle_list:
            obj = hnd_reg.Find(hnd)
            if not any([obj.IsTypeOf("Port"), obj.IsTypeOf("StreamBlock"),
                        obj.IsTypeOf("Project"), obj.IsTypeOf("StmTemplateConfig"),
                        obj.IsTypeOf("StmTemplateMix")]):
                return "Invalid handle type: " + obj.GetType() + \
                       ". L2 learning command only allows handles of type Port and StreamBlock"

    # The L3 learning command only allows handles of type Port, StreamBlock, Host,
    # Router, and EmulatedDevice
    if enable_l3:
        for hnd in handle_list:
            obj = hnd_reg.Find(hnd)
            if not any([obj.IsTypeOf("Port"), obj.IsTypeOf("StreamBlock"),
                        obj.IsTypeOf("EmulatedDevice"), obj.IsTypeOf("Host"),
                        obj.IsTypeOf("Router"), obj.IsTypeOf("Project"),
                        obj.IsTypeOf("StmTemplateMix"), obj.IsTypeOf("StmTemplateConfig")]):
                    return "Invalid handle type: " + obj.GetType() + \
                           ". Learning command only allows handles of type Port, " + \
                           "StreamBlock, Host, Router, and EmulatedDevice"
    return ""


def get_valid_handles(handle_list, tag_name_list):
    hnd_reg = CHandleRegistry.Instance()
    l2_obj_list = []
    l3_obj_list = []
    l2_handle_list = []
    l3_handle_list = []

    # Add object handles from the tag list to the handle list
    if len(tag_name_list) > 0:
        for obj in tag_utils.get_tagged_objects_from_string_names(tag_name_list):
            handle_list.append(obj.GetObjectHandle())

    # The L2 learning command only allows handles of type Port and StreamBlock
    # The L3 learning command only allows handles of type Port, StreamBlock, Host,
    # Router, and EmulatedDevice
    for hnd in handle_list:
        obj = hnd_reg.Find(hnd)
        if obj.IsTypeOf("Port") or obj.IsTypeOf("StreamBlock") or obj.IsTypeOf("Project"):
            l2_obj_list.append(obj)
            l3_obj_list.append(obj)
        elif obj.IsTypeOf("EmulatedDevice") or obj.IsTypeOf("Host") or obj.IsTypeOf("Router"):
            l3_obj_list.append(obj)
        elif obj.IsTypeOf("StmTemplateMix") or obj.IsTypeOf("StmTemplateConfig"):
                l2_obj_list.extend(dm_utils.get_class_objects([hnd], [],
                                                              ["Port",
                                                               "StreamBlock",
                                                               "Project"]))
                l3_obj_list.extend(dm_utils.get_class_objects([hnd], [],
                                                              ["Port",
                                                               "StreamBlock",
                                                               "Project",
                                                               "EmulatedDevice",
                                                               "Host",
                                                               "Router"]))

    for obj in dm_utils.sort_obj_list_by_handle(l2_obj_list):
        l2_handle_list.append(obj.GetObjectHandle())
    for obj in dm_utils.sort_obj_list_by_handle(l3_obj_list):
        l3_handle_list.append(obj.GetObjectHandle())
    return l2_handle_list, l3_handle_list


def reset():
    return True
