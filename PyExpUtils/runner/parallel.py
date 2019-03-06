def flagString(pairs):
    for pair in pairs:
        key, value = pair
        if value is not None:
            yield f'{key} {str(value)}'

def buildParallel(d):
    # required
    ex = d['executable']
    cores = d['cores']
    tasks = d['tasks']

    # make sure tasks is a string
    tasks = tasks if isinstance(tasks, str) else ' '.join(map(str, tasks))

    # optional
    delay = d.get('delay')

    # build parameter pairs
    pairs = [
        ('-j', cores),
        ('--delay', delay)
    ]

    # build parallel options
    ops = ' '.join(flagString(pairs))

    return f'parallel {ops} {ex} ::: {tasks}'
