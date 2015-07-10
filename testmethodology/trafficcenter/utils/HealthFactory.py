from StcIntPythonPL import *
import json
import ast
from spirent.core.utils.scriptable import AutoCommand
from .. import ResultSubscriber


class HealthFactory:
    def __init__(self, url, context, config, cmd):
        self.url = url
        self.context = context
        self.config = config
        self.cmd = cmd

    def subscribe(self):
        raise NotImplementedError("Please implement a subscription method")

    def dumps(self, data):
        return ast.literal_eval(json.dumps(data))

    def update_refresh_option(self):
        stcSys = CStcSystem.Instance()
        project = stcSys.GetObject("Project")
        resOptions = project.GetObject("ResultOptions")
        resOptions.Set("TimedRefreshResultViewMode", "PERIODIC")
        resOptions.Set("TimedRefreshInterval", 1)


class TrafficHealthFactory(HealthFactory):
    def subscribe(self):
        self.unsubscribe_threshould_result()
        self.handle_traffic_health()

    def unsubscribe_threshould_result(self):
        stcSys = CStcSystem.Instance()
        project = stcSys.GetObject("Project")
        ports = project.GetObjects("Port")

        for port in ports:
            ana = port.GetObject("Analyzer")
            results = ana.GetObjects("StreamThresholdResults")
            for res in results:
                ds = res.GetObject("ResultDataSet", RelationType.ReverseDir("resultchild"))
                if ds:
                    with AutoCommand("ResultDataSetUnsubscribeCommand") as cmd:
                        cmd.Set("ResultDataSet", ds.GetObjectHandle())
                        cmd.Execute()

    def handle_traffic_health(self):
        if len(self.config) == 0:
            return
        stcSys = CStcSystem.Instance()
        project = stcSys.GetObject("Project")
        self.update_refresh_option()

        hnds, attribute_list = self.create_result_filter(self.config)
        with AutoCommand("ResultsSubscribeCommand") as cmd:
            cmd.Set("parent", project.GetObjectHandle())
            cmd.Set("configType", "analyzer")
            cmd.Set("resultType", "streamthresholdresults")
            cmd.Set("viewAttributeList", attribute_list)
            cmd.SetCollection("resultParent", [project.GetObjectHandle()])
            cmd.SetCollection("filterList", hnds)
            cmd.Execute()

        subcription_attrs = ["StreamThresholdResults." + attr for attr in attribute_list.split()]

        with AutoCommand("SubscribePropertyChangeCommand") as sub_cmd:
            sub_cmd.Set("PropertyClassId", "StreamThresholdResults")
            sub_cmd.SetCollection("PropertyIdList", subcription_attrs)
            sub_cmd.Set("PublishUrl", self.dumps(self.url))
            sub_cmd.Set("Context", self.dumps(self.context))
            sub_cmd.Set("IncludeResultParent", True)
            sub_cmd.Execute()

    def create_result_filter(self, traffic_health):

        CUSTOM_NAME = "customfiltercount"
        count = 1
        filter_hnds = []
        counter_result_filter = []
        filters = []
        health_names = []

        ctor = CScriptableCreator()
        stcSys = CStcSystem.Instance()
        project = stcSys.GetObject("Project")

        for health in traffic_health:
            result_filter = ctor.Create("CounterResultFilter", project)
            filter_property = ctor.Create("CounterFilterProperty", result_filter)
            filter_property.Set("FilterDisplayName", self.dumps(health["name"]))
            filter_property.Set("PropertyOperand", self.dumps(health["name"]))
            filter_property.Set("ValueOperand", self.dumps(health["threshold"]))
            filter_property.Set("ComparisonOperator", self.dumps(health["condition"]))
            filter_hnds.append(result_filter.GetObjectHandle())
            filters.append(CUSTOM_NAME + str(count))
            counter_result_filter.append(result_filter.GetObjectHandle())
            health_names.append(str(health["name"]))
            count += 1

        filter_name = " ".join(filters)
        self.cmd.SetCollection("TrafficFilter", counter_result_filter)
        self.cmd.SetCollection("TrafficThresholdNames", health_names)
        return filter_hnds, filter_name


class SystemHealthFactory(HealthFactory):
    def subscribe(self):
        for health in self.config:
            self.subscribe_data_model(health)

    def subscribe_data_model(self, health_config):
        health_name = self.dumps(health_config["name"])

        if health_name == "PhysicalLinkFailure":
            self.subscribe_property_change("EthernetPhy", ["EthernetPhy.LinkStatus"], True)
        elif health_name == "ChassisTemperature":
            self.subscribe_property_change("PhysicalChassisTempStatus",
                                           ["PhysicalChassisTempStatus.HighestSensorStatus"])
        elif health_name == "NdFailure" or health_name == "ArpFailure":
            self.subscribe_property_change("ArpCache", ["ArpCache.ArpCacheData"])
        elif health_name == "PortLowMemory":
            pass
        elif health_name == "OverflowResults":
            self.subscribe_overflow_result()
        elif health_name == "PortTemperature":
            pass
        elif health_name == "DhcpFailure":
            self.subscribe_dhcp_result()

    def subscribe_property_change(self, classId, propertyList, enable_subclasses=False):
        with AutoCommand("SubscribePropertyChangeCommand") as sub_cmd:
            sub_cmd.Set("PropertyClassId", classId)
            sub_cmd.SetCollection("PropertyIdList", propertyList)
            sub_cmd.Set("PublishUrl", self.dumps(self.url))
            sub_cmd.Set("Context", self.dumps(self.context))
            sub_cmd.Set("IncludeResultParent", True)
            sub_cmd.Set("EnableSubClasses", enable_subclasses)
            sub_cmd.Execute()

    def subscribe_overflow_result(self):
        stcSys = CStcSystem.Instance()
        project = stcSys.GetObject("Project")

        with AutoCommand("ResultsSubscribeCommand") as cmd:
            cmd.Set("parent", project.GetObjectHandle())
            cmd.Set("configType", "analyzer")
            cmd.Set("resultType", "overflowresults")
            cmd.Execute()

        self.subscribe_property_change("overflowresults",
                                       ["overflowresults.SigFrameCount"])

    def subscribe_dhcp_result(self):
        plLogger = PLLogger.GetLogger("subscribe_dhcp_result")
        plLogger.LogInfo("subscribe_dhcp_result: ")
        stcSys = CStcSystem.Instance()
        project = stcSys.GetObject("Project")

        with AutoCommand("ResultsSubscribeCommand") as cmd:
            cmd.Set("parent", project.GetObjectHandle())
            cmd.Set("configType", "dhcpv4blockconfig")
            cmd.Set("resultType", "dhcpv4blockresults")
            cmd.Execute()

        self.subscribe_property_change("dhcpv4blockresults",
                                       ["dhcpv4blockresults.totalfailedcount"])


class TrafficDRVHealthFactory(HealthFactory):
    def subscribe(self):
        if len(self.config) == 0:
            return

        self.update_refresh_option()

        with AutoCommand("SubscribePropertyChangeCommand") as sub_cmd:
            sub_cmd.Set("PropertyClassId", "DynamicResultView")
            sub_cmd.SetCollection("PropertyIdList", ["DynamicResultView.ResultCount"])
            sub_cmd.Set("PublishUrl", self.dumps(self.url))
            sub_cmd.Set("Context", self.dumps(self.context))
            sub_cmd.Set("IncludeResultParent", True)
            sub_cmd.Execute()

        health_drv_names = []
        health_drvs = []
        for health in self.config:
            drv = ResultSubscriber.subscribe(health['name'])
            if drv is not None:
                health_drv_names.append(str(health['name']))
                health_drvs.append(drv.GetObjectHandle())
                with AutoCommand("TimedRefreshResumeCommand") as refresh_cmd:
                    refresh_cmd.Set("DynamicResultView", drv.GetObjectHandle())
                    refresh_cmd.Execute()

        self.cmd.SetCollection('TrafficDrvNames', health_drv_names)
        self.cmd.SetCollection('TrafficDrvs', health_drvs)
