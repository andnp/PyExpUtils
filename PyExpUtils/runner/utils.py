from typing import Any, Callable, Dict, Generator, Iterable, List, TypeVar
from PyExpUtils.models.ExperimentDescription import ExperimentDescription, loadExperiment
from PyExpUtils.results.pandas import detectMissingIndices

T = TypeVar('T')
def print_progress(size: int, it: Iterable[T]) -> Generator[T, Any, None]:
    m_width = 0
    for i, v in enumerate(it):
        msg = f'{i + 1}/{size}'
        m_width = max(m_width, len(msg))
        print(' ' * m_width, end='\r')
        print(msg, end='\r')
        if i - 1 == size:
            print()
        yield v

def approximate_cost(jobs: int, cores_per_job: int, mem_per_core: float, hours: float):
    total_cores = jobs * cores_per_job
    mem_in_gb = mem_per_core / 1024
    core_equivalents = total_cores * max(mem_in_gb / 4, 1)

    core_hours = core_equivalents * hours
    core_years = core_hours / (24 * 365)

    return core_years

def gather_missing_indices(experiment_paths: Iterable[str], runs: int, result_file: str, loader: Callable[[str], ExperimentDescription] = loadExperiment, base: str = './'):
    path_to_indices: Dict[str, List[int]] = {}

    for path in experiment_paths:
        exp = loader(path)

        indices = detectMissingIndices(exp, runs, result_file, base=base)
        indices = sorted(indices)
        path_to_indices[path] = indices

        size = exp.numPermutations() * runs
        print(path, f'{len(indices)} / {size}')

    return path_to_indices
