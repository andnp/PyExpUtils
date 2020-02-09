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
    sshloginfile = d.get('sshloginfile')

    # build parameter pairs
    pairs = [
        ('-j', cores),
        ('--delay', delay),
        ('--sshloginfile', sshloginfile),
    ]

    # build parallel options
    ops = ' '.join(flagString(pairs))

    if len(tasks) == 0:
        return None

    return f'parallel {ops} {ex} ::: {tasks}'
