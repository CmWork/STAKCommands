from StcIntPythonPL import *
import traceback
from spirent.core.utils.scriptable import AutoCommand
from results.ResultInterface import ResultInterface
import spirent.methodology.results.ProviderDataGenerator as pdg
from spirent.methodology.results.ProviderConst import ProviderConst as pc


def validate():
    return ""


def clean_up():
    with AutoCommand('chassisDisconnectAll') as cmd:
        cmd.Execute()
    with AutoCommand('ApplyToILCommand') as cmd:
        cmd.Execute()


def run():
    exit_state = True
    logger = PLLogger.GetLogger('methodology')
    try:
        sequencer = CStcSystem.Instance().GetObject("Sequencer")
        if sequencer is None:
            raise Exception('Unable to find sequencer object.')

        if sequencer.Get('StoppedCommand') == 0:
            # case 1: normal end of test
            logger.LogInfo("Calling end test.")
            ResultInterface.end_test()
        else:
            if sequencer.Get('TestState').lower() != 'failed':
                # case 2: sequencer manually stopped by user
                logger.LogInfo("Calling stop test.")
                ResultInterface.stop_test()
            else:
                # case 3: sequencer stopped on error
                logger.LogInfo("Calling stop test with error.")
                seq_status = sequencer.Get('Status')
                pdg.submit_sequencer_execution_error(seq_status)
                ResultInterface.stop_test()

    except Exception, e:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        pdg.submit_command_execution_error('EndOfTestCommand',
                                           str(e),
                                           stack_trace)
        ResultInterface.stop_test()
        exit_state = False
    except:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        pdg.submit_command_execution_error('EndOfTestCommand',
                                           pc.UNKNOWN_EXCEPTION_MESSAGE,
                                           tack_trace)
        ResultInterface.stop_test()
        exit_state = False

    clean_up()
    return exit_state


def reset():
    return True
