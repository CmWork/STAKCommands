
dummy_verify_result_passed = {
    "class": "tableDrvDrilldown",
    "dataFormat": "table",
    "info": {
        "name": "MyTestDrv-passed",
        "summarizationObject": "Project.Name",
        "reportGroup": 'SUMMARY'
    },
    "status": {
        "promoteVerdict": True,
        "execStatus": "completed",
        "verdict": "passed",
        "verdictExplanation": "Not available"
    },
    "data": {
        "columnNames": [
            "First",
            "Second"
        ],
        "rows": [
            [
                4,
                6
            ]
        ],
        "links": [
            {
                "tag": "Port.Name",
                "linkData": {
                    "class": "drillDownResults",
                    "dataFormat": "table",
                    "info": {
                        "summarizationObject": "Port.Name"
                    },
                    "data": {
                        "columnNames": [
                            "First",
                            "Second"
                        ],
                        "rows": [
                            [
                                1,
                                2
                            ],
                            [
                                3,
                                4
                            ]
                        ]
                    }
                }
            }
        ]
    }
}


dummy_verify_result_failed = {
    "class": "tableDrvDrilldown",
    "dataFormat": "table",
    "info": {
        "name": "MyTestDrv-failed",
        "summarizationObject": "Project.Name",
        "reportGroup": 'GROUP_1'
    },
    "status": {
        "promoteVerdict": True,
        "execStatus": "completed",
        "verdict": "failed",
        "verdictExplanation": "Not available"
    },
    "data": {
        "columnNames": [
            "First",
            "Second"
        ],
        "rows": [
            [
                4,
                6
            ]
        ],
        "links": [
            {
                "tag": "Port.Name",
                "linkData": {
                    "class": "drillDownResults",
                    "dataFormat": "table",
                    "info": {
                        "summarizationObject": "Port.Name"
                    },
                    "data": {
                        "columnNames": [
                            "First",
                            "Second"
                        ],
                        "rows": [
                            [
                                1,
                                2
                            ],
                            [
                                3,
                                4
                            ]
                        ]
                    }
                }
            }
        ]
    }
}

result_group_2_1 = {
    "class": "mynote",
    "dataFormat": "none",
    "info": {
        "name": "result_group_2_1",
        "reportGroup": 'GROUP_2'
    }
}

result_group_2_2 = {
    "class": "mynote",
    "dataFormat": "none",
    "info": {
        "name": "result_group_2_2",
        "reportGroup": 'GROUP_2'
    }
}

result_group_2_3 = {
    "class": "mynote",
    "dataFormat": "none",
    "info": {
        "name": "result_group_2_3",
        "reportGroup": 'GROUP_2'
    }
}

result_group_5 = {
    "class": "mynote",
    "dataFormat": "none",
    "info": {
        "name": "result_group_5",
        "reportGroup": 'GROUP_5'
    }
}

# status string with exe complete and rest none
status_exec_complete_1 = '{"execStatus":"completed","verdict":"none","verdictExplanation":"none"}'
status_pass_2 = '{"execStatus":"completed","verdict":"passed",' + \
    '"verdictExplanation":"All of the conditions of the sub-tests have passed."}'
status_exec_stopped_3 = '{"execStatus":"stopped","verdict":"none","verdictExplanation":"none"}'
status_pass_stopped_4 = '{"execStatus":"stopped","verdict":"passed",' + \
    '"verdictExplanation":"All of the conditions of the sub-tests have passed."}'
status_exec_complete_5 = '{"execStatus":"completed","verdict":"none",' + \
    '"verdictExplanation":"Not Defined"}'
status_iterator_6 = '{"promoteVerdict":true,"execStatus":"completed",' + \
    '"verdict":"none","verdictExplanation":"Not Defined"}'
status_failed_7 = '{"execStatus":"completed","verdict":"failed",' + \
    '"verdictExplanation":"Not Defined"}'
status_exec_stopped_8 = '{"execStatus":"stopped","verdict":"none",' + \
    '"verdictExplanation":"Not Defined"}'

data_empty_1 = '{"tag":"all_groups","children":[]}'

# file lists
result_file_list_1 = ['testReport.json',
                      'Iteration-FrameSize-64-id-1.json',
                      'Iteration-FrameSize-128-id-2.json',
                      'Iteration-FrameSize-256-id-3.json'
                      ]

result_file_list_2 = ['testReport.json',
                      'Iteration-FrameSize-64-Load-10-id-1.json',
                      'Iteration-FrameSize-64-Load-20-id-2.json',
                      'Iteration-FrameSize-128-Load-10-id-1.json',
                      'Iteration-FrameSize-128-Load-20-id-2.json',
                      'Iteration-FrameSize-256-Load-10-id-1.json',
                      'Iteration-FrameSize-256-Load-20-id-2.json'
                      ]

result_file_list_3 = ['testReport.json',
                      'Iteration-FrameSize-64-Load-10-id-1.json'
                      ]

result_file_list_4 = ['testReport.json',
                      'Iteration-FrameSize-64-Load-10-id-1.json',
                      'Iteration-FrameSize-64-Load-20-id-2.json'
                      ]
