import re

with open("/tmp/fifo") as fifo:
    cache = {}
    for line in fifo:
        match = re.search(r"(201903\d{2}) (\d{2}:\d{2}:\d{2})", line)
        if match:
            date = match.group(1)
            hour = match.group(2)
            target = "./fixData/%s_%s" % (date, hour)

            if target not in cache:
                cache[target] = open(target, 'a')

            cache.get(target).write(line)
