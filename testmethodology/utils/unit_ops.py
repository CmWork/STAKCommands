load_unit_map = {
    'PERCENT_LINE_RATE': '%',
    'BITS_PER_SECOND': 'bps',
    'KILOBITS_PER_SECOND': 'Kbps',
    'MEGABITS_PER_SECOND': 'Mbps',
    'FRAMES_PER_SECOND': 'Fps'
}


def get_load_unit_abbr(load_enum):
    if load_enum not in load_unit_map:
        raise ValueError('Invalid load type: ' + load_enum)
    return load_unit_map[load_enum]
