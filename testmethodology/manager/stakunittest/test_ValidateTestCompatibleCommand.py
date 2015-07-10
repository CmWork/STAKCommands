from StcIntPythonPL import *
from ..ValidateTestCompatibleCommand import parseConfigTree


class TestValidateTestCompatibleCommand:

    test_sequencer = '''<StcSystem id="1" serializationBase="true"
InSimulationMode="FALSE"
UseSmbMessaging="FALSE"
ApplicationName="TestCenter"
Active="TRUE"
LocalActive="TRUE"
Name="StcSystem 1">
<Sequencer id="8"
CommandList="1922 1923 1929 1930 1931 1932 1933 1934 1935 1936 1937"
BreakpointList=""
DisabledCommandList=""
CleanupCommand="9"
Active="TRUE"
LocalActive="TRUE"
Name="Sequencer">
<Relation type="SequencerFinalizeType" target="9"/>
<L2TestBreakLinkCommand id="1922"
Port="2"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="L2Test: Break Link 1">
</L2TestBreakLinkCommand>
<L2TestBreakLinkCommand id="1923"
Port="2"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="L2Test: Break Link 2">
</L2TestBreakLinkCommand>
<ArpNdUpdateArpCacheCommand id="1929"
HandleList="2"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: ArpNdUpdateArpCacheCommand 1">
</ArpNdUpdateArpCacheCommand>
<ArpNdStartCommand id="1930"
HandleList="2"
WaitForArpToFinish="TRUE"
ForceArp="TRUE"
Report=""
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: Start ArpNd 1">
</ArpNdStartCommand>
<ArpNdStartOnAllDevicesCommand id="1931"
PortList="2"
WaitForArpToFinish="TRUE"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: Start ArpNd On All Devices 1">
</ArpNdStartOnAllDevicesCommand>
<L2LearningStartCommand id="1932"
L2LearningOption="TX_RX"
HandleList="2"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: Start L2 Learning 1">
</L2LearningStartCommand>
<ArpNdStopCommand id="1933"
HandleList="2"
Report=""
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: Stop ArpNd 1">
</ArpNdStopCommand>
</Sequencer>
</StcSystem>'''

    test_sequencer_fail = '''<StcSystem id="1" serializationBase="true"
InSimulationMode="FALSE"
UseSmbMessaging="FALSE"
ApplicationName="TestCenter"
Active="TRUE"
LocalActive="TRUE"
Name="StcSystem 1">
<Sequencer id="8"
CommandList="1922 1923 1929 1930 1931 1932 1933 1934 1935 1936 1937"
BreakpointList=""
DisabledCommandList=""
CleanupCommand="9"
Active="TRUE"
LocalActive="TRUE"
Name="Sequencer">
<Relation type="SequencerFinalizeType" target="9"/>
<L2TestBreakLinkCommand id="1922"
Port="2"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="L2Test: Break Link 1">
</L2TestBreakLinkCommand>
<L2TestBreakLinkCommand id="1923"
Port="2"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="L2Test: Break Link 2">
</L2TestBreakLinkCommand>
<ArpNdUpdateArpCacheCommand id="1929"
HandleList="2"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: ArpNdUpdateArpCacheCommand 1">
</ArpNdUpdateArpCacheCommand>
<ArpNdStartCommand id="1930"
HandleList="2"
WaitForArpToFinish="TRUE"
ForceArp="TRUE"
Report=""
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: Start ArpNd 1">
</ArpNdStartCommand>
<ArpNdStartOnAllDevicesCommand id="1931"
PortList="2"
WaitForArpToFinish="TRUE"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: Start ArpNd On All Devices 1">
</ArpNdStartOnAllDevicesCommand>
<L2LearningStartCommand id="1932"
L2LearningOption="TX_RX"
HandleList="2"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: Start L2 Learning 1">
</L2LearningStartCommand>
<ArpNdStopCommand id="1933"
HandleList="2"
Report=""
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Learning: Stop ArpNd 1">
</ArpNdStopCommand>
<spirent.methodology.DummyCommand id="1937"
fileName="methodology.zip"
CommandName=""
PackageName="spirent"
ErrorOnFailure="TRUE"
AutoDestroy="FALSE"
ExecuteSynchronous="FALSE"
ProgressEnable="TRUE"
ProgressIsSafeCancel="TRUE"
Active="TRUE"
LocalActive="TRUE"
Name="Test Methodology: ImportTestCommand 1">
</spirent.methodology.DummyCommand>
</Sequencer>
</StcSystem>'''

    file_name = "testcompatible.xml"

    def test_validate_xml(self, stc):
        t = TestValidateTestCompatibleCommand

        f = open(t.file_name, "w")
        f.write(t.test_sequencer)
        f.close()

        res = parseConfigTree(t.file_name)

        assert res is True

    def test_validate_xml_fail(self, stc):
        t = TestValidateTestCompatibleCommand

        f = open(t.file_name, "w")
        f.write(t.test_sequencer_fail)
        f.close()

        res = parseConfigTree(t.file_name)

        assert res is False
