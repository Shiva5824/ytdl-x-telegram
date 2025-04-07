def format_bytes(size):
    power = 1024
    n = 0
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    while size > power and n < 4:
        size /= power
        n += 1
    return f"{round(size,2)} {units[n]}"