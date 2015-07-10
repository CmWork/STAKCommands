from StcIntPythonPL import *


def validate(Duration):
    return ''


def run(Duration):

    # Temporary create two ports for now
    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")
    ports = project.GetObjects("Port")

    for port in ports:
        gen = port.GetObject("Generator")
        if gen:
            gen_cfg = gen.GetObject("GeneratorConfig")
            gen_cfg.Set("DurationMode", "SECONDS")
            gen_cfg.Set("Duration", float(Duration))

    return True


def reset():
    return True
