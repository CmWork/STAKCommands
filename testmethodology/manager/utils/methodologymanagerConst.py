import os.path


class MethodologyManagerConst(object):
    MM_METHODOLOGY = "Methodology"
    MM_PACKAGES = "Packages"
    MM_SCRIPTS = "Scripts"
    MM_TEMPLATES = "Templates"
    MM_TEST_METH_DIR = os.path.join(MM_METHODOLOGY, MM_PACKAGES)
    MM_SCRIPTS_DIR = os.path.join(MM_METHODOLOGY, MM_SCRIPTS)
    MM_TEST_CASE_SUBDIR = "TestCases"
    MM_TEMPLATE_DIR = os.path.join(MM_METHODOLOGY, MM_TEMPLATES)

    MM_META_FILE_NAME = "meta.txml"
    MM_META_JSON_FILE_NAME = "meta.json"
    MM_SEQUENCER_FILE_NAME = "sequencer.xml"

    MM_STM_EXT = ".stm"
