import glob

MODULES = ['models', 'runner', 'results', 'utils']

doc_str = """# PyExpUtils

"""

def scanFile(f):
    for line in f.readlines():


py_paths = glob.glob('PyExpUtils/**/*.py', recursive=True)
py_paths = filter(lambda path: '__init__.py' in path, py_paths)

split_paths = {}
for module in MODULES:
    split_paths[module] = []

for path in py_paths:
    parts = path.split('/')
    module = parts[1]
    arr = split_paths.get(module, [])
    arr.append(path)

for module in MODULES:
    for path in split_paths[module]:
        f = open(path, 'r')

