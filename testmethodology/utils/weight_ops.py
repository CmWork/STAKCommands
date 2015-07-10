import math


def allocate_weighted_list(total_count, weight_list, percentage=True,
                           allow_fraction=False):
    '''
        total_count is an integer value
        weight_list is a list of float weight values to distribute total_count
        percentage is True if the weight list is a list of percentages
    '''
    if math.modf(total_count)[0] != 0.0:
        allow_fraction = True
    total_sum = 100.0 if percentage is True else float(sum(weight_list))
    total_count_expected = float(total_count)
    if percentage is True and sum(weight_list) > 100.0:
        raise ValueError('Total sum of percentage weights exceeds 100')
    if percentage is True and sum(weight_list) < 100.0:
        total_count_expected = float(total_count) * sum(weight_list) / 100.0
    tup_list = []
    for idx, weight in enumerate(weight_list):
        # Add two tuples
        ent_tup = (idx,) + math.modf(float(total_count) * float(weight) / total_sum)
        tup_list.append(ent_tup)
    # Sort by 2nd tuple element (remainder)
    tup_list.sort(key=lambda ent: ent[1], reverse=True)
    if allow_fraction is False:
        sum_whole = int(sum(ent[2] for ent in tup_list))
    else:
        sum_whole = sum(ent[1] + ent[2] for ent in tup_list)
    if sum_whole != total_count_expected:
        delta = total_count_expected - sum_whole
        if allow_fraction:
            # If it is a percentage, and the total does not add up to 100, the
            # delta needs to be reduced by the "missing amount"
            # Add the remaining fractional part
            tup_list[0] = (tup_list[0][0],) + \
                (tup_list[0][1] + delta, tup_list[0][2])
        # The amount to distribute should be less than how many there are
        elif delta < len(tup_list):
            # Sum of remainders to be distributed, biggest remainder first
            for idx in range(len(tup_list)):
                # Increment (concatenate two tuples)
                tup_list[idx] = tup_list[idx][0:2] + (tup_list[idx][2] + 1,)
                delta = delta - 1
                if delta <= 0:
                    break
    # Sort by index, restoring order
    tup_list.sort(key=lambda ent: ent[0])
    if allow_fraction:
        return [ent[1] + ent[2] for ent in tup_list]
    else:
        return [ent[2] for ent in tup_list]


def parse_weight_string(weight, allow_fraction=False):
    err_str = ""
    is_percent = False
    act_val = 0.0

    # weight should be a string
    if not isinstance(weight, basestring):
        err_str = "weight must be a string."
        return is_percent, act_val, err_str

    # Determine if it is a percentage
    if weight[-1] == "%":
        is_percent = True
        number_part = weight[0:-1]
    else:
        number_part = weight

    # Find the number (as a float)
    try:
        act_val = float(number_part)
    except:
        err_str = "Could not convert " + str(weight) + \
            " into a number (ie 5 or 3.2) or a percent " + \
            "(ie 5% or 3.2%)."
        return is_percent, act_val, err_str

    # Determine if the number if fractions aren't allowed
    if not is_percent:
        if not allow_fraction:
            if math.floor(act_val) != act_val:
                err_str = "Weight must be an integer value.  " + \
                    str(act_val) + " is not supported."
                return is_percent, act_val, err_str
            act_val = math.floor(act_val)

    return is_percent, act_val, err_str
