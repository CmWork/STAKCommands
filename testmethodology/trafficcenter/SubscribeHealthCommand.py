from StcIntPythonPL import *
import json
from utils import HealthFactory as HF
from utils import traffic_health_type_lookup


def get_this_cmd():
    '''
    Get this Command instance from the
    HandleRegistry for setting output properties,
    status, progress, etc.
    '''
    hndReg = CHandleRegistry.Instance()
    try:
        thisCommand = hndReg.Find(__commandHandle__)
    except NameError:
        return None
    return thisCommand


def validate(HealthConfig):
    return ''


def run(HealthConfig):
    data = json.loads(HealthConfig)
    health = data["health"]
    traffic = health["traffic"]
    traffic_threshold = [traffic_health for traffic_health
                         in traffic
                         if traffic_health_type_lookup.LOOKUP_MAP.get(
                             traffic_health["name"]
                             ) == 'thr']
    traffic_drv = [traffic_health for traffic_health
                   in traffic
                   if traffic_health_type_lookup.LOOKUP_MAP.get(
                       traffic_health["name"]
                       ) == 'drv']
    system = health["system"]
    cb = data["callback_info"]
    traffic_cb = cb["traffic"]
    traffic_url = traffic_cb["url"]
    traffic_context = traffic_cb["context"]
    tf = HF.TrafficHealthFactory(traffic_url,
                                 traffic_context,
                                 traffic_threshold,
                                 get_this_cmd())
    tf.subscribe()
    drv_cb = cb["drv"]
    drv_url = drv_cb["url"]
    drv_context = drv_cb["context"]
    tdf = HF.TrafficDRVHealthFactory(drv_url,
                                     drv_context,
                                     traffic_drv,
                                     get_this_cmd())
    tdf.subscribe()
    system_cb = cb["system"]
    system_url = system_cb["url"]
    system_context = system_cb["context"]
    sf = HF.SystemHealthFactory(system_url,
                                system_context,
                                system,
                                get_this_cmd())
    sf.subscribe()
    return True


def reset():
    return True
