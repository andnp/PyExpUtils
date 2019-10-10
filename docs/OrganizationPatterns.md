## Structure
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
`scripts/` will hold things like job scheduling and exploratory data analysis scripts (though those sometimes go in another `analysis/` folder depending on the project).

### Experiments
The `experiments/` folder contains all of the experiment source code and experiment description datafiles.
It additionally contains brief experiment write-ups, usually in markdown.

#### Experiment Folders
The structure of this directory is generally flat.
It contains a list of folders with experiment short names.
For example:
```
experiments/
experiments/overfit
experiments/covariateShift
...
```

I do **not** have version numbers in these folders.
Inevitably, the experiments will change with time.
These changes are checked into the version control software (git), and recorded in a log (more on that momentarily).

Inside each of the individual experiment folders, I have the description datafiles and the experiment entry script.

#### Entry Script
Every experiment contains its own entry script.
This is the one part of the codebase where copy/paste is accepted and encouraged.
These scripts should be minimal, and should only "plug-in" the pieces developed in `src/`.
An example:
```python
from src.dataloader import dataloader
from src.ANN import ANN

data = dataloader.MNIST()
ann = ANN()

ann.train(data)

accuracy_train = ann.evaluate(data.train)
accuracy_test = ann.evaluate(data.test)

saveFile('test.csv', accuracy_test)
saveFile('train.csv', accuracy_train)
```
This is the file that will be called at the command-line: `python experiments/overfit/overfit.py`.

#### Experiment Descriptions
All experiment description files should be stored in JSON format.
These files describe the parameter sweeps that are inherent with most, if not all, machine learning experiments.
They also describe manipulations of experiment level parameters (as opposed to only algorithm meta-parameters).

An example:
```JSON
{
    "algorithm": "ANN",
    "dataset": "MNIST",
    "metaParameters": {
        "layers": [
            { "type": "dense", "units": 256, "transfer": ["linear", "relu", "sigmoid"] }
        ],
        "useDictionary": false,
        "dictionaryWeight": [0.01]
    },
    "limitSamples": 1000,
    "optimizer": {
        "type": "rmsprop",
        "stepsize": 0.001
    }
}
```

In the above example, `metaParameters` specifies algorithm meta-parameters.
The values inside an array at the lowest level of the object will be swept over.
In this case, `layers` and `transfer` are both array values.
`layers` is not at the bottom of the object, but `transfer` is; only `transfer` will be swept over.
This means that this experiment description describes 3 different models, one with a `linear` transfer, one with a `relu` transfer, and one with a `sigmoid` transfer.

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

#### Analysis
Each of the experiments folders will contain a set of analysis scripts.
These analysis files will read in the generated experiment data and produce the final plots and tables.

They should take **no** command-line arguments.
If I have a set of results, running one of these scripts should produce a near-publish-ready plot or table.
The no arguments restriction reduces cognitive load when running these scripts months later to reproduce results.

These are another case where copy/paste is okay, as many of these scripts will be quite similar.
As with the entry files, these should be minimal and high-level.
Low-level functions should be (intelligently) abstracted out in the `src/` directory.

#### Experiment Write-ups
In every experiment directory, there should be a living write-up document.
This document keeps a _complete_ history of all experiment trials, both failures and successes.
In my experience, each of these write-ups will contain a dozen failures and a single success (because once you have a successfully experiment, generally you stop running it again!)

The structure of these files is still in flux for me, however there are consistent key details that should be included.
1) The trial number - how many times have you attempted this experiment?
2) A textual description of the experiment that should have enough details to reproduce without the code.
3) The hypothesis being tested.
4) The list of open questions, and open issues.
5) The list of follow-up questions after running a trial - often times when running an experiment, auxiliary questions become clear. This is a great place to look when trying to come up with future research directions!
6) A textual description of the outcome for each trial - usually an explanation of what went wrong.
7) The outputs of the `analysis` scripts for each trial.
8) The commit hash for the repo (and any important sub-repos) when each trial was run.

An example:
```markdown
# Overfit
A long description of this experiment.
Why am I measuring overfitting, and how?
What are my goals?
How does this tie into the larger project?

## Hypothesis
What do I expect will happen?
What does success look like, and how do I measure that?

## Open Questions
1) How does my choice of optimizer affect the results?
2) Am I running enough epochs, or will the ANN stop overfitting after a certain point?

## Follow-up Questions
1) Do these effects hold across other datasets?
2) Would a model with skip connections overfit as badly?

## Trials
### Trial 00
This trial tests with 300 epochs.
It failed to run long enough, as the test accuracy continued to decrease sharply at epoch 300.
I should run again with many more epochs, perhaps 600.
#### Results
[Learning curves](./trials/trial-00_test-train.svg)
```

#### Experiment Log
The final piece to the experiment folder is a table-of-contents or experiment log.
This is a top level markdown file in the `experiments/` folder that specifies what each of the subfolders contains.
After a month or two, there will be old experiments that you forget about.
This file should be a reminder of what has happened in the past.

It usually looks like:
```markdown
# Experiment Log

## Experiments
### Overfit 3/1/19
**status**: on-going
**path**: `overfit/`

### Covariate Shift 9/15/18
**status**: complete
**path**: `covariateShift/`
```
Note that entries should be in reverse order of age (newest first, oldest last).

#### Putting it all together
The `experiments` directory should look like:
```
experiments/
experiments/toc.md
experiments/overfit
experiments/overfit/results.md
experiments/overfit/overfit.py
experiments/overfit/learning_curve.py
experiments/overfit/ann.json
experiments/overfit/logistic_regression.json
experiments/overfit/trials/trial-00_test-train.svg
```

### Results
The results directory contains all of the **raw** results from experiments.
The subfolders should be the experiment short names (e.g. `results/overfit` using the above example).
This is usually a git submodule.

This folder can become unwieldy with many many files.
As such a git hosting service like github will not work.
Usually I host a git repo on my personal server.
I am actively investigating better solutions here.

