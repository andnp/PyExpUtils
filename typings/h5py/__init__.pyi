from typing import Any, List

class File:
    def __init__(self, path: str, mode: str) -> None: ...

    # context manager
    def __enter__(self) -> File: ...  # noqa: F821
    def __exit__(self, type: Any, value: Any, traceback: Any) -> None: ...

    # groups
    def create_group(self, name: str) -> Group: ...  # noqa: F821

    # act like dict
    def __getitem__(self, name: str) -> Any: ...  # noqa: F821
    def __contains__(self, name: str) -> bool: ...
    def keys(self) -> List[str]: ...

    # act like file
    def close(self) -> None: ...

class Group:
    # datasets
    def create_dataset(self, name: str, data: Any = ..., compression: str = ...) -> None: ...

class Dataset:
    pass
