
class MethodologyManagerUtestConst(object):

    # Constants for TXML unit tests
    MM_UTEST_FILE_NAME = "mm_unit_test.xml"
    MM_UTEST_DISPLAY_NAME = "Unit Test Display Name"
    MM_UTEST_METH_KEY = "UNITTEST"
    MM_UTEST_DESCRIPTION = "Unit Test Description"
    MM_UTEST_INSTANCE = "UnitTestInstance"
    MM_UTEST_VERSION = "1.0"
    MM_UTEST_LABEL1 = "RFC2544"
    MM_UTEST_LABEL2 = "Benchmark"
    MM_UTEST_LABELS = "<labels><label>" + MM_UTEST_LABEL1 + "</label><label>" + \
                      MM_UTEST_LABEL2 + "</label></labels>"
    MM_UTEST_HEADER = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + \
                      "<test>" + \
                      "<testInfo " + \
                      "displayName=\"" + MM_UTEST_DISPLAY_NAME + "\" " + \
                      "description=\"" + MM_UTEST_DESCRIPTION + "\" " + \
                      "testCaseName=\"" + MM_UTEST_INSTANCE + "\" " + \
                      "version=\"" + MM_UTEST_VERSION + "\" " + \
                      "methKey=\"" + MM_UTEST_METH_KEY + "\" " + \
                      "testCaseKey=\"\" " + \
                      ">" + \
                      MM_UTEST_LABELS + \
                      "</testInfo>"
    MM_UTEST_FOOTER = "</test>"
    MM_UTEST_TEST_TAG = "test"
    MM_UTEST_TESTINFO_TAG = "testInfo"
