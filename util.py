def parse_time(time):
    time_parts = time.split(':')
    return int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])