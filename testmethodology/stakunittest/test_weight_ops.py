import sys
import os
import traceback
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent',
                             'methodology'))
import spirent.methodology.utils.weight_ops as weight


# Unit test from Brady and Felma's shelved changelist
def test_allocate_count():
    device_count = 99
    percentage_list = [1, 98, 1]
    device_list = weight.allocate_weighted_list(device_count, percentage_list)
    assert device_list == [1, 97, 1]

    device_count = 11
    percentage_list = [25, 75]
    device_list = weight.allocate_weighted_list(device_count, percentage_list)
    assert device_list == [3, 8]

    device_count = 99
    percentage_list = [25, 50, 25]
    device_list = weight.allocate_weighted_list(device_count, percentage_list)
    assert device_list == [25, 49, 25]

    device_count = 99
    percentage_list = [98, 1, 1]
    device_list = weight.allocate_weighted_list(device_count, percentage_list)
    assert device_list == [97, 1, 1]

    device_count = 100
    percentage_list = [95, 1, 1, 1, 2]
    device_list = weight.allocate_weighted_list(device_count, percentage_list)
    assert device_list == [95, 1, 1, 1, 2]

    device_count = 99
    percentage_list = [1, 1, 95, 1, 2]
    device_list = weight.allocate_weighted_list(device_count, percentage_list)
    assert device_list == [1, 1, 94, 1, 2]

    device_count = 100
    percentage_list = [.1, .2, 99, .3, .4]
    device_list = weight.allocate_weighted_list(device_count, percentage_list)
    assert device_list == [0, 0, 99, 0, 1]

    device_count = 100
    percentage_list = [.1, .1, 99.5, .1, .2]
    device_list = weight.allocate_weighted_list(device_count, percentage_list)
    assert device_list == [0, 0, 100, 0, 0]

    device_count = 100
    percentage_list = [10, 20.5, 30.3, 38.2]
    device_list = weight.allocate_weighted_list(device_count, percentage_list)
    # Note that the sum for this is 99, so we have only 1 extra, originally it
    # was [10, 21, 31, 38]
    assert device_list == [10, 21, 30, 38]


def test_allocate_exceed():
    device_count = 99
    percentage_list = [1, 98, 2]
    fail_msg = ''
    try:
        weight.allocate_weighted_list(device_count, percentage_list)
    except:
        exc_info = sys.exc_info()
        fail_list = traceback.format_exception_only(exc_info[0],
                                                    exc_info[1])
        fail_msg = fail_list[0] if len(fail_list) == 1 else '\n'.join(fail_list)
    if fail_msg == '':
        raise AssertionError('function did not fail as expected')
    if 'weights exceeds 100' not in fail_msg:
        raise AssertionError('function failed with unexpected exception: "' +
                             fail_msg + '"')


def test_allocate_total_not_100():
    device_count = 50
    weight_list = [20, 40]
    device_list = weight.allocate_weighted_list(device_count, weight_list)
    assert device_list == [10, 20]


def test_allocate_non_percent():
    device_count = 100
    weight_list = [2, 4]
    device_list = weight.allocate_weighted_list(device_count, weight_list,
                                                percentage=False)
    assert device_list == [33, 67]

    device_count = 100
    weight_list = [4, 4, 4]
    device_list = weight.allocate_weighted_list(device_count, weight_list,
                                                percentage=False)
    assert device_list == [34, 33, 33]


def test_parse_weight_string():
    is_percent, act_val, err_str = weight.parse_weight_string("10")
    assert err_str == ""
    assert not is_percent
    assert act_val == 10

    is_percent, act_val, err_str = weight.parse_weight_string("10.0%")
    assert err_str == ""
    assert is_percent
    assert act_val == 10

    is_percent, act_val, err_str = weight.parse_weight_string("10.1 %")
    assert err_str == ""
    assert is_percent
    assert act_val == 10.1

    is_percent, act_val, err_str = weight.parse_weight_string(10.0)
    assert err_str == "weight must be a string."

    is_percent, act_val, err_str = weight.parse_weight_string("abc.123%")
    assert "Could not convert abc.123% into a number " in err_str

    is_percent, act_val, err_str = weight.parse_weight_string("abc.123")
    assert "Could not convert abc.123 into a number " in err_str

    is_percent, act_val, err_str = weight.parse_weight_string(
        "15.6", allow_fraction=False)
    assert "Weight must be an integer value." in err_str

    is_percent, act_val, err_str = weight.parse_weight_string(
        "15.6", allow_fraction=True)
    assert err_str == ""
    assert act_val == 15.6
    assert not is_percent

    is_percent, act_val, err_str = weight.parse_weight_string(
        "15.6%", allow_fraction=False)
    assert err_str == ""
    assert is_percent
    assert act_val == 15.6
