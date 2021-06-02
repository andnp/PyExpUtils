# Repo Organization
I structure all of my machine learning experiments in the same way.
This common structure lowers the cognitive cost of switching between projects.
The structure specification has been a work in progress over the past few years, but has finally converged to a reasonably stable point.

My experiment codebase always looks like:
```
src/
tests/
scripts/
config.json

experiments/
results/
```

The `src/`, `tests/`, and `scripts/` folders hold all of the common source code.
This includes things like dataset loaders, RL environments, and ML model code.
`scripts/` will hold things like job scheduling, sanity checking, or other various one-off scripting needs.
As much as I can, I try to keep all common code in the `src/` folder to encourage reuse.

## src
The `src/` (short for source code) contains all of the primary research code for the repo.
It usually has many subfolders and follows roughly the same organization.
```
src/
src/analysis/
src/agents/
src/environments/
src/problems/
src/utils/
src/main.py
```

The `analysis/` folder contains the shared low-level functions used within my data analysis scripts for processing the results of an experiment.
It might have functions for slicing and dicing data before plotting, color definitions for each algorithm, or other utility code specific to results analysis.

The `agents/` (or sometimes `algorithms/`) folder contains the learning algorithms that I am testing.
Usually each algorithm has a singular file (e.g. `DQN.py`) and often there are a couple of base-class files (`BaseAgent.py` for example).
Reuse code where you can.
If two algorithms differ only in one line in their update (think `SARSA` vs. `Expected SARSA`), then try to have only appr. one line of code in one of those files; the remainder of the code being shared with the other file.

The `environments/` (or sometimes `datasets/`) folder contains code for interacting with environments (or datasets).
I have one file for each environment/dataset, or occasionally a single file for similar environments (like `gym.py` for loading any gym environment, or `minatar.py` for all minatar games).
Often these files contain no more than 5-10 lines of code which translates whatever interface into my preferred RL-Glue interface (or dataset loading interface when I'm doing [un]supervised learning experiments).

The `problems/` folder contains one file for every "problem" setting.
This can often be redundant with `environments/` and skipped entirely.
One use case is Baird's Counter-example which includes a specific feature representation and weight initialization scheme, which do not clearly belong in the `environment/` code nor do they clearly belong anywhere else.
So the `problems/bairds.py` file would tie together the representation, agent initialization, and environment in one common API for all "problems".
Another use case would be a 5-state random walk environment which has 3 different feature representations; thus has 3 defined "problems" for one environment.

The `utils/` folder contains several code files for various miscellaneous utility functions.
Often this might include `random.py`, `dict.py`, `array.py`, etc. for manipulating random numbers, dictionaries, and numpy arrays respectively.
When these utilities are used often in my codebase, they often get promoted to here (PyExpUtils) where they live in the appropriately named `utiles/` folder of this library.

The `main.py` file is the general entry point for running experiments.
It is extremely common to have multiple entry points that define different types of experiments (for instance one that does online evaluation, one that does offline evaluation, and one that measures variance of returns or something).
The **only** top-level files are entry point scripts, no other code file is ever allowed at the top-level.
This strictness helps to maintain a nice clean repo that contains an obvious "starting" point for the code.

## Experiments
The `experiments/` folder contains experiment specific scripts, experiment description meta-data, plots, and analysis code.
It may contain brief experiment write-ups, usually in markdown.

The structure of this directory is generally flat.
It contains a list of folders with experiment short names.
For example:
```
experiments/
experiments/overfit
experiments/covariateShift
...
```
with two experiments: `overfit` and `covariateShift`.

I do **not** have version numbers in these folders.
Inevitably, the experiments will change with time.
These changes are checked into the version control software (git) and thus version keeping via file naming is redundant.

### Experiment Descriptions
All experiment description files are stored in JSON format.
The format is less important (and other formats can be easily used), but the practice of keeping serialized experiment descriptions is very important.
These files describe all of the high-level details of the experiment that is being run; including parameters that are being manipulated, algorithms being tested, datasets or environments being used, algorithm-specific parameter settings, experiment-specific parameter settings, etc.

By creating and relying on these serialized description files, instead equivalent of hot-code within a script, it is much easier to track changes in an experiment and confirm that expectations are being met when starting an experiment.
Consider the following example.
I want to test my algorithm on all of the datasets registered in the codebase, so I use a script that generates a new experiment for each dataset.
I generate results, do analysis, get some plots.
Then later, I delete one of the datasets that is registered and run the experiment script again.
Now I am running a totally different set of experiments silently, without any part of the process warning me that the outcome results (e.g. the plots) will look different due to a down-stream code change.

An example:
```JSON
{
    "algorithm": "ANN",
    "dataset": "MNIST",
    "metaParameters": {
        "layers": [
            { "type": "dense", "units": 256, "transfer": "relu" },
            { "type": "dense", "units": 256, "transfer": ["linear", "relu", "sigmoid"] }
        ],
        "useDictionary": false,
        "dictionaryWeight": [0.01],
        "optimizer": {
            "type": "rmsprop",
            "stepsize": 0.001
        }
    },
    "limitSamples": 1000,
    "experiment": {
        "addNoise": true,
        "shufflePixels": true
    }
}
```

In the above example, `metaParameters` specifies algorithm meta-parameters.
The values inside an array at the lowest level of the object will be swept over.
In this case, `layers` and `transfer` are both array values.
`layers` is not at the bottom of the object, but `transfer` is; only `transfer` will be swept over.
This means that this experiment description describes 3 different models, one where the final layer uses a `linear` transfer, one with a `relu` transfer, and one with a `sigmoid` transfer.

Bottom level parameters can be singleton values or length 1 arrays if they are not to be swept.
That is
```JSON
{ "units": 256 }
```
and
```JSON
{ "units": [256] }
```
are equivalent.
The first is just syntactic sugar for the second, as it is a common case.

### Analysis
Each of the experiments folders will contain a set of analysis scripts.
These analysis files will read in the generated experiment data and produce the final plots and tables.

They should take **no** command-line arguments.
If I have a set of results, running one of these scripts should produce a near-publish-ready plot or table.
The no arguments restriction reduces cognitive load when running these scripts months later to reproduce results.

These are a case where copy/paste is okay, as many of these scripts will be quite similar.
As with the entry files, these should be minimal and high-level.
Low-level functions should be (intelligently) abstracted out in the `src/` directory.

## Results
The results directory contains all of the **raw** results from experiments.
The subfolders should be the experiment short names (e.g. `results/overfit` using the above example).
This is usually a git submodule.

This folder can become unwieldy with many many files.
As such a git hosting service like github will not work.
Usually I host a git repo on my personal server.
I am actively investigating better solutions here.
