class EnumExecStatus():
    none = 'none'
    created = 'created'
    running = 'running'
    completed = 'completed'
    error = 'error'
    stopped = 'stopped'


class EnumVerdict(object):
    none = 'none'
    passed = 'passed'
    failed = 'failed'

    @staticmethod
    def do_override_verdict(verdict, new_verdict):
        """New verdict overwrite on equal or higher.
        """
        if verdict == EnumVerdict.none or new_verdict == EnumVerdict.failed:
            return True
        elif new_verdict == EnumVerdict.passed:
            if verdict == EnumVerdict.failed:
                return False
            else:
                return True
        elif verdict == EnumVerdict.passed:
            if new_verdict == EnumVerdict.failed:
                return True
            else:
                return False
        elif verdict == EnumVerdict.failed:
            return False
        else:
            return True


class EnumDataFormat(object):
    group = 'group'
    table = 'table'
    note = 'note'
    chart = 'chart'
    none = 'none'


class EnumDataClass(object):
    table_drv_drilldown = 'tableDrvDrilldown'
    drill_down_results = 'drillDownResults'
    error_summary_details = 'errorMessage'
    table_db_query = 'tableDbQuery'
    iteration_result = 'iterationResult'
    iterator_result = 'iteratorResult'
    test_report = 'testReport'
    iteration_report = 'iterationReport'
    result_group = 'resultGroup'
    methodology_chart = 'MethodologyChart'
