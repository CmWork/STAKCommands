from StcIntPythonPL import *
import os
import json
from drv_def.system_drv import SYSTEM_DRV_MAP
from spirent.core.utils.scriptable import AutoCommand

drv_def_path = os.path.join(os.path.dirname(__file__), 'drv_def')
drv_def_ext = 'json'

logger = PLLogger.GetLogger(
    'spirent.trafficcenter.ResultSubscriber'
    )

registered = {}
project = CStcSystem.Instance().GetObject('project')
ctor = CScriptableCreator()
for drv in project.GetObjects('DynamicResultView'):
    registered[drv.Get('Name')] = drv

hndReg = CHandleRegistry.Instance()


def initDrv(drvname):
    drv = ctor.Create('DynamicResultView', project)
    registered[drvname] = drv.GetObjectHandle()
    drv.Set('Name', str(drvname))
    return drv


def loadConfig(drvname):
    drv = initDrv(drvname)
    prq = ctor.Create('PresentationResultQuery', drv)
    prq.SetCollection('FromObjects', [str(project.GetObjectHandle())])
    try:
        with open(
            os.path.join(
                drv_def_path, drvname + '.' + drv_def_ext),
                'r') as f:
            conf = json.load(f)
            for k, v in conf.items():
                if type(v) == list:
                    prq.SetCollection(str(k), [str(e) for e in v])
                else:
                    prq.SetCollection(str(k), str(v))
    except IOError as e:
        logger.LogWarn("I/O error({0}): {1}".format(e.errno, e.strerror))
        drv.MarkDelete()
        return None
    return drv


def loadSystemConfig(drvname):
    uri = SYSTEM_DRV_MAP.get(drvname)
    if uri is None:
        logger.LogInfo('system result view %s not found' % str(drvname))
        return None
    drv = initDrv(drvname)
    try:
        with AutoCommand("LoadFromTemplateCommand") as template_cmd:
            template_cmd.Set("TemplateUri", uri)
            template_cmd.Set("Config", drv.GetObjectHandle())
            template_cmd.Execute()
    except Exception as e:
        logger.LogError('Error in loading drv template %s' % e)
        drv.MarkDelete()
        return None
    return drv


def subscribe(drvname):
    drv = None
    need_load = True
    if drvname in registered:
        drv_hnd = registered[drvname]
        drv = hndReg.Find(drv_hnd)
        if drv is not None and not drv.IsDeleted():
            need_load = False
    if need_load:
        try:
            drv = loadSystemConfig(drvname)
            if drv is None:
                drv = loadConfig(drvname)
        except Exception as e:
            logger.LogError('Error in subscribe %s: %s' % (str(drvname), e))
            return None

    if drv is not None:
        try:
            with AutoCommand('subscribeDynamicResultView') as subCmd:
                subCmd.Set('DynamicResultView', str(drv.GetObjectHandle()))
                subCmd.Execute()
        except Exception as e:
            if 'already subscribed' in e.message:
                logger.LogWarn('DRV %s already subscribed' % str(drvname))
                return drv
            else:
                logger.LogError('Error in subscribe %s: %s' % (str(drvname), e))
                return None
        logger.LogInfo('Subscribed DRV %s' % drv.Get('Name'))

    return drv


def unsubscribe(drvname):
    if drvname in registered:
        try:
            with AutoCommand('unsubscribeDynamicResultView') as subCmd:
                subCmd.Set('DynamicResultView',
                           str(registered[drvname]))
                subCmd.Execute()
            return True
        except Exception as e:
            logger.LogError('Error in unsubscribe %s' % e)
    return False
