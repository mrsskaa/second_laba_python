from abc import ABC, abstractmethod
from os import PathLike
from typing import Literal

from src.enums import FileReadMode


class OSConsoleServiceBase(ABC):
    @abstractmethod
    def ls(self, path: PathLike[str] | str) -> list[str]: ...

    @abstractmethod
    def cat(
        self,
        filename: PathLike | str,
        mode: Literal[FileReadMode.string, FileReadMode.bytes] = FileReadMode.string,
    ) -> str | bytes: ...
