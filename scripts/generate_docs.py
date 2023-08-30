import glob
import re

MODULES = ['models', 'runner', 'results', 'utils']

doc_str = """# PyExpUtils

Short for python experiment utilities.
This is a collection of scripts and machine learning experiment management tools that I use whenever I have to use python.

For a more complete discussion on my organization patterns for research codebases, [look in the docs](docs/OrganizationPatterns.md).

## This lib
Maintaining a rigorous experiment structure can be labor intensive.
As such, I've automated out many of the common pieces that I use in my research.

### Parameter Permutations
Experiments are encoded within JSON files.
The JSON files should contain all of the information necessary to reproduce an experiment, including all parameters swept.
Each of the parameter sweep specifications leads to a set of parameter permutations.
Imagine the case where you are sweeping over 2 meta-parameters:
```json
{
    "metaParameters": {
        "alpha": [0.01, 0.02, 0.04],
        "epsilon": [0.1, 0.2, 0.3]
    }
}
```
Here there are 9 total possible permutations: `{alpha: 0.01, epsilon: 0.1}`, `{alpha: 0.01, epsilon: 0.2}`, ...

These are indexed by a single numeric value.
To run each permutation once, simply execute indices `i \\in [0..8]`.
To run each permutation twice, multiply by 2: `i \\in [0..17]`.
In general for `n` runs and `p` permutations: `i \\in [0..(n*p - 1)]`.


"""

def getName(line):
    line = line.strip()
    line = line.replace('def ', '')
    line = line.replace('class ', '')
    line = re.sub(r'\W*\(.*\).*:*', '', line)
    line = line.replace(':', '')
    return line

def scanFile(f):
    in_doc = False
    tabs = 0
    get_method = False
    buffer = []
    total = {}
    for line in f.readlines():
        if get_method:
            if '@' in line:
                continue
            get_method = False
            name = getName(line)
            total[name] = buffer
            tabs = 0
            buffer = []
            continue

        if not in_doc and '"""doc' in line:
            in_doc = True
            # count the number of whitespaces to offset all lines in docs by
            m = re.match(r'\W*', line) or ['']
            tabs = len(m[0]) - 3
            continue

        if not in_doc:
            continue

        if '"""' in line:
            in_doc = False
            get_method = True
            continue

        line = line[tabs:]
        buffer.append(line)

    return total


py_paths = glob.glob('PyExpUtils/**/*.py', recursive=True)
py_paths = filter(lambda path: '__init__.py' not in path, py_paths)

split_paths = {}
for module in MODULES:
    split_paths[module] = []

for path in py_paths:
    parts = path.split('/')
    module = parts[1]
    arr = split_paths.get(module, [])
    arr.append(path)

for module in MODULES:
    doc_str += f"## {module}\n"

    init = open(f'PyExpUtils/{module}/__init__.py', 'r')
    init_str = ''
    start_read = False
    for line in init.readlines():
        if '"""doc' in line:
            start_read = True
            continue

        if '"""' in line:
            start_read = False
            continue

        if start_read:
            init_str += line

    doc_str += init_str
    init.close()

    for path in split_paths[module]:
        f = open(path, 'r')
        docs = scanFile(f)
        if len(docs):
            doc_str += f"### {path}\n"
        for method in docs:
            doc_str += f"**{method}**:\n\n"
            doc_str += ''.join(docs[method]) + '\n\n'
        f.close()

with open('README.md', 'w') as f:
    f.write(doc_str)
