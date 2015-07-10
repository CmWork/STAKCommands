from StcIntPythonPL import *
import re
from spirent.methodology.results.ResultInterface import ResultInterface


TM_PKG = "spirent.methodology"
TC_PKG = "spirent.trafficcenter"


# Gets the commands of type IteratorConfigCommand from the input cmd_hnd_list
def get_configurator_cmds(cmd_hnd_list):
    hnd_reg = CHandleRegistry.Instance()

    config_cmd_list = []
    for cmd_hnd in cmd_hnd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if (cmd is None):
            continue
        if cmd.IsTypeOf(TM_PKG + ".IteratorConfigCommand"):
            config_cmd_list.append(cmd)
    return config_cmd_list


# Gets the commands of type IteratorValidateCommand from the input cmd_hnd_list
def get_validator_cmds(cmd_hnd_list):
    hnd_reg = CHandleRegistry.Instance()

    validate_cmd_list = []
    for cmd_hnd in cmd_hnd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if (cmd is None):
            continue
        if cmd.IsTypeOf(TM_PKG + ".IteratorValidateCommand"):
            validate_cmd_list.append(cmd)
    return validate_cmd_list


# Builds the property chains for Iteration and CurrVal from the iterator to the configurator
def build_iterator_to_configurator_property_chains(iter_cmd, config_cmd_list):
    ctor = CScriptableCreator()
    for config_cmd in config_cmd_list:
        # Set up property chaining between the Object Iterator and the Iterator Config commands
        # Iteration
        chain_cmd = ctor.CreateCommand("AddPropertyChainingCommand")
        chain_cmd.SetCollection("SourcePropertyIdList",
                                [TM_PKG + ".ObjectIteratorCommand.Iteration"])
        chain_cmd.SetCollection("SourceCommandList", [iter_cmd.GetObjectHandle()])
        chain_cmd.SetCollection("TargetPropertyIdList",
                                [TM_PKG + ".IteratorConfigCommand.Iteration"])
        chain_cmd.SetCollection("TargetCommandList", [config_cmd.GetObjectHandle()])
        chain_cmd.Execute()
        chain_cmd.MarkDelete()

        # CurrVal
        chain_cmd = ctor.CreateCommand("AddPropertyChainingCommand")
        chain_cmd.SetCollection("SourcePropertyIdList",
                                [TM_PKG + ".IteratorCommand.CurrVal"])
        chain_cmd.SetCollection("SourceCommandList", [iter_cmd.GetObjectHandle()])
        chain_cmd.SetCollection("TargetPropertyIdList",
                                [TM_PKG + ".IteratorConfigCommand.CurrVal"])
        chain_cmd.SetCollection("TargetCommandList", [config_cmd.GetObjectHandle()])
        chain_cmd.Execute()
        chain_cmd.MarkDelete()


# Builds the property chains for Iteration from the iterator to the validator
def build_iterator_to_validator_property_chains(iter_cmd, valid_cmd):
    ctor = CScriptableCreator()
    # Set up property chaining between the Iterator command and the Iterator Validate command
    # Iteration
    iter_cmd_iteration_id = TM_PKG + ".IteratorCommand.Iteration"
    chain_cmd = ctor.CreateCommand("AddPropertyChainingCommand")
    chain_cmd.SetCollection("SourcePropertyIdList", [iter_cmd_iteration_id])
    chain_cmd.SetCollection("SourceCommandList", [iter_cmd.GetObjectHandle()])
    chain_cmd.SetCollection("TargetPropertyIdList",
                            [TM_PKG + ".IteratorValidateCommand.Iteration"])
    chain_cmd.SetCollection("TargetCommandList", [valid_cmd.GetObjectHandle()])
    chain_cmd.Execute()
    chain_cmd.MarkDelete()


# Builds the property chains for Verdict from the validator to the iterator
def build_validator_to_iterator_property_chains(valid_cmd, iter_cmd):
    ctor = CScriptableCreator()

    # Set up property chaining between the Iterator Validate command and the Iterator command
    # Verdict
    iter_cmd_verdict_id = TM_PKG + ".IteratorCommand.PrevIterVerdict"

    chain_cmd = ctor.CreateCommand("AddPropertyChainingCommand")
    chain_cmd.SetCollection("SourcePropertyIdList",
                            [TM_PKG + ".IteratorValidateCommand.Verdict"])
    chain_cmd.SetCollection("SourceCommandList", [valid_cmd.GetObjectHandle()])
    chain_cmd.SetCollection("TargetPropertyIdList", [iter_cmd_verdict_id])
    chain_cmd.SetCollection("TargetCommandList", [iter_cmd.GetObjectHandle()])
    chain_cmd.Execute()
    chain_cmd.MarkDelete()


# Determine if the SequencerWhileCommand's expression command is an iterator
# Returns an iterator or an iterate command or None if something else
def get_sequencer_while_expression_cmd(cmd):
    hnd_reg = CHandleRegistry.Instance()
    if cmd.IsTypeOf("SequencerWhileCommand"):
        arg_cmd_handle = cmd.Get("ExpressionCommand")
        arg_cmd = hnd_reg.Find(arg_cmd_handle)
        if arg_cmd is None:
            return None
        else:
            if arg_cmd.IsTypeOf(TM_PKG + ".IteratorCommand"):
                return arg_cmd
    return None


# Builds property chains for the iterator, configurator, and validators within a single
# IterationGroupCommand.  Does not look any further into contained IterationGroupCommands.
def build_iteration_group_property_chains(group_cmd):
    hnd_reg = CHandleRegistry.Instance()
    plLogger = PLLogger.GetLogger('methodology')
    if group_cmd is None:
        err_str = "Input group_cmd is None"
        plLogger.LogError(err_str)
        return

    if not group_cmd.IsTypeOf(TM_PKG + ".IterationGroupCommand"):
        plLogger.LogError(group_cmd.Get("Name") +
                          " is not type of " + TM_PKG +
                          ".IterationGroupCommand")
        return

    # Find the Iterator, Configurator, and Validator commands
    cmd_hnd_list = group_cmd.GetCollection("CommandList")
    plLogger.LogInfo("cmd_hnd_list is: " + str(cmd_hnd_list))

    iter_cmd = None
    while_cmd = None
    for cmd_hnd in cmd_hnd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            plLogger.LogWarn("Skipping invalid command!")
            continue
        if cmd.IsTypeOf("SequencerWhileCommand"):
            iter_cmd = get_sequencer_while_expression_cmd(cmd)
        if iter_cmd is not None:
            while_cmd = cmd
            break
    if iter_cmd is None:
        plLogger.LogError("Could not find a SequencerWhileCommand " +
                          "with an IteratorCommand.")
        return
    if while_cmd is None:
        plLogger.LogError("Could not find a SequencerWhileCommand")
        return

    config_cmd_list = get_configurator_cmds(
        while_cmd.GetCollection("CommandList"))
    valid_cmd_list = get_validator_cmds(
        while_cmd.GetCollection("CommandList"))

    if iter_cmd.IsTypeOf(TM_PKG + ".IteratorCommand"):
        if len(config_cmd_list) < 1:
            plLogger.LogError("Could not find any IteratorConfigCommands")
            return False

    plLogger.LogInfo("iter_cmd: " + iter_cmd.Get("Name"))
    plLogger.LogInfo("config_cmd_list has: " + str(len(config_cmd_list)))
    plLogger.LogInfo("valid_cmd_list has: " + str(len(valid_cmd_list)))

    # Build property chains
    build_iterator_to_configurator_property_chains(iter_cmd, config_cmd_list)

    # FIXME:
    # How do we support more than one validator?
    # More importantly, does it make sense to support???
    # Answer: Yes, it does make sense to support.
    #   Put into a Validator Group Command
    if len(valid_cmd_list) > 0:
        build_iterator_to_validator_property_chains(iter_cmd, valid_cmd_list[0])
        build_validator_to_iterator_property_chains(valid_cmd_list[0], iter_cmd)

    # FIXME:
    # Move this into a separate function.  It does not
    # belong in this one.
    # Pass the ObjectList to the next nested IterationGroupCommand
    for cmd_hnd in while_cmd.GetCollection("CommandList"):
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            plLogger.LogWarn("WARNING: Skipping invalid handle in " +
                             "SequencerWhileCommand's CommandList")
            continue
        if cmd.IsTypeOf(TM_PKG + ".IterationGroupCommand"):
            cmd.SetCollection("ObjectList", group_cmd.GetCollection("ObjectList"))


# Finds the while command that uses the iteratorcommand
def get_iteration_group_iterator_while_cmd(group_cmd):
    hnd_reg = CHandleRegistry.Instance()
    plLogger = PLLogger.GetLogger('methodology')
    if group_cmd is None:
        plLogger.LogWarn("group_cmd is None")
        return

    if not group_cmd.IsTypeOf(TM_PKG + ".IterationGroupCommand"):
        plLogger.LogError(group_cmd.Get("Name") + " is not type of " + TM_PKG +
                          ".IterationGroupCommand")
        plLogger.LogError(" It is type of: " + str(group_cmd.GetType()))
        return

    # Find the while command
    # It must be located at the same level (not contained in another while)
    while_cmd = None
    for cmd_hnd in group_cmd.GetCollection("CommandList"):
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            plLogger.LogWarn("invalid command discovered...skipping it")
            continue
        if cmd.IsTypeOf("SequencerWhileCommand"):
            iter_cmd = get_sequencer_while_expression_cmd(cmd)
        if iter_cmd is not None:
            while_cmd = cmd
            break
    return while_cmd


# Returns a list of the commands of the given type
# (cmd_string_id) in the cmd_hnd_list
def get_cmds_recursive(cmd_hnd_list, cmd_string_id):
    hnd_reg = CHandleRegistry.Instance()
    plLogger = PLLogger.GetLogger('methodology')

    ret_cmd_list = []

    for cmd_hnd in cmd_hnd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            continue
        if cmd.IsTypeOf("SequencerGroupCommand") or \
           cmd.IsTypeOf("stak.StakGroupCommand"):
            # Recurse into the SequencerGroupCommand's CommandList
            # Determine if this is a SequencerWhileCommand first

            if cmd.IsTypeOf("SequencerWhileCommand"):
                plLogger.LogInfo("found a while command in the input cmd_hnd_list")

                # Check whether or not the expression contains an iterator
                exp_cmd_hnd = cmd.Get("ExpressionCommand")
                if exp_cmd_hnd is not None:
                    exp_cmd = hnd_reg.Find(exp_cmd_hnd)
                    if exp_cmd is not None and exp_cmd.IsTypeOf(cmd_string_id):
                        ret_cmd_list.append(exp_cmd)

            # Handle all other commands in the SequencerGroupCommand
            ret_cmd_list = ret_cmd_list + \
                get_cmds_recursive(cmd.GetCollection("CommandList"),
                                   cmd_string_id)
        if cmd.IsTypeOf(cmd_string_id):
            ret_cmd_list.append(cmd)
        for cmd in ret_cmd_list:
            plLogger.LogInfo("  - " + str(cmd.GetType()))
    return ret_cmd_list


# Returns a list of all the IteratorConfigCommands
# found in the input cmd_hnd_list.
def get_all_configurator_cmds(cmd_hnd_list):

    ret_cmd_list = []
    ret_cmd_list = ret_cmd_list + \
        get_cmds_recursive(cmd_hnd_list, TM_PKG + ".IteratorConfigCommand")

    return ret_cmd_list


def debug_print_cmd_hnd_list(cmd_hnd_list):
    plLogger = PLLogger.GetLogger('methodology')
    hnd_reg = CHandleRegistry.Instance()
    plLogger.LogInfo("cmd_hnd_list: ")
    for cmd_hnd in cmd_hnd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            plLogger.LogInfo(" skipping cmd with handle " +
                             str(cmd_hnd) + " as not found in handle registry")
            continue
        plLogger.LogInfo(" cmd is: " + str(cmd.GetType()))


# Build property chains between iterator, configurator, validator, and recurse as necessary
def build_iteration_framework_property_chains(cmd_hnd_list):
    hnd_reg = CHandleRegistry.Instance()
    plLogger = PLLogger.GetLogger('methodology')

    debug_print_cmd_hnd_list(cmd_hnd_list)

    for cmd_hnd in cmd_hnd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            continue
        if cmd.IsTypeOf("SequencerGroupCommand"):
            # May need to recurse into the SequencerGroupCommand's CommandList
            # Determine if this is a SequencerWhileCommand first

            if cmd.IsTypeOf("SequencerWhileCommand"):

                # Check whether or not the expression contains an iterator
                exp_cmd = get_sequencer_while_expression_cmd(cmd)

                if exp_cmd is not None:
                    iter_cmd = None
                    if exp_cmd.IsTypeOf(TM_PKG + ".IteratorCommand"):
                        iter_cmd = exp_cmd

                    sub_cmd_list = cmd.GetCollection("CommandList")
                    config_cmd_list = get_configurator_cmds(sub_cmd_list)
                    valid_cmd_list = get_validator_cmds(sub_cmd_list)

                    # Build property chains
                    if iter_cmd is None:
                        plLogger.LogError("Was unable to find an IteratorCommand.")
                        return
                    if config_cmd_list is None:
                        plLogger.LogError("Was unable to find"
                                          " an IteratorConfigCommand.")
                        return

                    build_iterator_to_configurator_property_chains(
                        iter_cmd, config_cmd_list)

                    if len(valid_cmd_list):
                        # FIXME:
                        # Can only handle one validate command at the time
                        if len(valid_cmd_list) > 1:
                            plLogger.LogWarn("Iteration framework can only "
                                             "handle one validator command.")
                        valid_cmd = valid_cmd_list[0]

                        build_iterator_to_validator_property_chains(iter_cmd,
                                                                    valid_cmd)
                        build_validator_to_iterator_property_chains(valid_cmd,
                                                                    iter_cmd)

            # Handle all other commands in the SequencerGroupCommand
            build_iteration_framework_property_chains(
                cmd.GetCollection("CommandList"))
    return


def parse_iterate_mode_input(curr_val):
    # Strip all whitespace
    curr_val = "".join(curr_val.split())

    # In order to make the iterators for frame size and load easier to use,
    # we can assume that if a single integer/float value is passed in, the
    # type is fixed.  This allows a user to specify start/step/end instead
    # of a list of fixed(x) values.

    # Int check
    try:
        int(curr_val)
        return {"type": "fixed", "start": curr_val}
    except ValueError:
        pass

    # Float check
    try:
        float(curr_val)
        return {"type": "fixed", "start": curr_val}
    except ValueError:
        pass

    # Regular expression patterns
    fixed_pattern = re.compile("fixed\((.*?)\)")
    incr_pattern = re.compile("incr\((.*?),(.*?),(.*?)\)")
    rand_pattern = re.compile("rand\((.*?),(.*?)\)")
    imix_pattern = re.compile("imix\((.*?)\)")

    fixed_match = fixed_pattern.search(curr_val)
    incr_match = incr_pattern.search(curr_val)
    rand_match = rand_pattern.search(curr_val)
    imix_match = imix_pattern.search(curr_val)

    if fixed_match is not None:
        return {"type": "fixed", "start": fixed_match.group(1)}
    if incr_match is not None:
        return {"type": "incr", "start": incr_match.group(1),
                "step": incr_match.group(2), "end": incr_match.group(3)}
    if rand_match is not None:
        return {"type": "rand", "start": rand_match.group(1), "end": rand_match.group(2)}
    if imix_match is not None:
        return {"type": "imix", "name": imix_match.group(1)}

    return None


def update_results_with_current_value(iterating_property,
                                      current_value,
                                      iteration_id,
                                      cmd_obj):
    """
    Update current iteration value to results framework.
    iterating_property: Framesize, load etc
    """
    pkg = "spirent.methodology"
    prop_chain_list = cmd_obj.GetObjects("PropertyChainingConfig",
                                         RelationType("PropertyChain", 1))
    iter_obj = None
    # Get the iterator handle (follow the reverse property chain...)
    for prop_chain in prop_chain_list:
        src_obj = prop_chain.GetParent()
        if src_obj.IsTypeOf(pkg + ".IteratorCommand"):
            iter_obj = src_obj
            break
    if iter_obj is not None:
        ResultInterface.set_iterator_current_value(iter_obj.GetObjectHandle(),
                                                   iterating_property,
                                                   current_value,
                                                   iteration_id)
