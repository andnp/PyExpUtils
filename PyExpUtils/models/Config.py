import json
from typing import Optional
from PyExpUtils.utils.fp import once

"""doc
Experiment utility configuration file.
Specifies global configuration settings:
 - *save_path*: directory format where experimental results will be stored
 - *log_path*: directory where log files will be saved (e.g. stacktraces during experiments)
 - *experiment_directory*: root directory where all of the experiment description files are located

The config file should be at the root level of the repository and should be named `config.json`.
```
.git
.gitignore
tests/
scripts/
src/
config.json
```

An example configuration file:
```json
{
    "save_path": "results/{name}/{environment}/{agent}/{params}",
    "log_path": "~/scratch/.logs",
    "experiment_directory": "experiments"
}
```
"""
class Config:
    def __init__(self):
        with open('config.json', 'r') as f:
            d = json.load(f)

        self.save_path: str = d['save_path']
        self.log_path: str = d.get('log_path', '.logs')
        self.experiment_directory: Optional[str] = d.get('experiment_directory', 'experiments')

"""doc
Memoized global configuration loader.
Will read `config.json` from (only once) and return a Config object.
```python
config = getConfig()
print(config.save_path) # -> 'results'
```
"""
@once
def getConfig():
    return Config()
