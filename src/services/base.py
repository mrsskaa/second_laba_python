from abc import ABC, abstractmethod
from os import PathLike
from typing import Literal

from src.enums import FileReadMode, FileDisplayMode

class OSConsoleServiceBase(ABC):
    @abstractmethod
    def ls(self, path: PathLike[str] | str, display_mode: FileDisplayMode = FileDisplayMode.simple) -> list[str]:
        """
        Абстрактный метод для отображения содержимого директории.
        :param path: Путь к директории для отображения
                     Может быть строкой "C:/Users" или объектом Path
        :param display_mode: Режим отображения (простой или подробный)
                             simple - только имена
                             detailed - с размером, датой, правами
        :return: Список строк с информацией о файлах и директориях
                 Каждая строка заканчивается переносом строки \n
        """
        ...

    @abstractmethod
    def cat(self, filename: PathLike | str, mode: Literal[FileReadMode.string, FileReadMode.bytes] = FileReadMode.string)->str | bytes:
        """
        Абстрактный метод для чтения и отображения содержимого файла.

        Что делает?
        - Читает содержимое файла
        - Возвращает его в виде строки или байтов

        :param filename: Путь к файлу для чтения
                         Может быть строкой или объектом Path
        :param mode: Режим чтения файла (текстовый или бинарный)
                     FileReadMode.string - читает как текст (UTF-8)
                     FileReadMode.bytes - читает как байты
        :return: Содержимое файла в виде строки или байтов

        Почему абстрактный?
        - Разные ОС могут по-разному работать с файлами
        - Нужна разная обработка ошибок для разных ОС
        """
        # ... означает, что метод не имеет реализации
        # Дочерние классы ОБЯЗАНЫ реализовать этот метод
        ...

    @abstractmethod
    def cd(self, path: PathLike[str] | str)->str:
        """
        Абстрактный метод для перехода в указанный каталог (смена рабочей директории).

        Что делает?
        - Переходит в указанную директорию
        - Поддерживает специальные пути (. , ~)
        - Возвращает новый абсолютный путь

        :param path: Путь к директории для перехода
                     Может быть относительным или абсолютным
                     . - текущая директория
                     .. - родительская директория (на уровень выше)
                     ~ - домашняя директория пользователя
        :return: Абсолютный путь к новой рабочей директории

        Почему абстрактный?
        - Разные ОС могут по-разному работать с путями
        - Нужна разная обработка ошибок для разных ОС

        :raises FileNotFoundError: Если директория не существует
        :raises NotADirectoryError: Если путь не является директорией
        """
        # ... означает, что метод не имеет реализации
        # Дочерние классы ОБЯЗАНЫ реализовать этот метод
        ...

    @abstractmethod
    def cp(self, src: PathLike[str] | str, dst: PathLike[str] | str, recursive: bool = False) -> None:
        """
        Абстрактный метод для копирования файла или каталога.

        :param src: Путь к исходному файлу/каталогу
        :param dst: Путь к месту назначения (файл или существующий каталог)
        :param recursive: Рекурсивно копировать каталоги (как -r/-г)
        :raises FileNotFoundError: Если источник не существует
        :raises IsADirectoryError: Если источник каталог без recursive=True
        :raises PermissionError: Если недостаточно прав
        :raises OSError: Прочие ошибки файловой системы
        """
        ...

    @abstractmethod
    def mv(self, src: PathLike[str] | str, dst: PathLike[str] | str) -> None:
        """
        Абстрактный метод для перемещения/переименования файла или каталога.

        Поддерживает перемещение в существующий каталог и переименование.

        :param src: Источник (файл или каталог)
        :param dst: Назначение (файл/каталог/новое имя)
        :raises FileNotFoundError: Если источник не существует
        :raises PermissionError: Если недостаточно прав
        :raises OSError: Прочие ошибки файловой системы
        """
        ...

    @abstractmethod
    def rm(self, target: PathLike[str] | str, recursive: bool = False) -> None:
        """
        Абстрактный метод для удаления файла/каталога.

        Ограничения:
        - Запрещено удалять корень (/) и родительский каталог (..)

        :param target: Путь к удаляемому объекту
        :param recursive: Рекурсивное удаление каталогов (-r/-г)
        """
        ...

    @abstractmethod
    def zip(self, path: PathLike[str] | str, path_arch: PathLike[str] | str) -> None:
        """
        Абстрактный метод для создания zip-архива из каталога.

        :param path: Путь к каталогу-источнику для упаковки
        :param path_arch: Путь к результирующему ZIP-файлу
        """
        ...

    @abstractmethod
    def unzip(self, path_arch: PathLike[str] | str, res: PathLike[str] | str | None = None) -> None:
        """
        Абстрактный метод для распаковки ZIP-архива.

        :param path_arch: Путь к ZIP-архиву
        :param res: Папка назначения; если None — используется текущая рабочая директория
        :raises FileNotFoundError: Если архив не существует
        :raises OSError: Прочие ошибки файловой системы
        """
        ...

    @abstractmethod
    def tar_dir(self, path_file: PathLike[str] | str, path_arch: PathLike[str] | str) -> None:
        """
        Абстрактный метод для создания TAR.GZ архива из каталога.

        :param path_file: Путь к каталогу‑источнику для упаковки
        :param path_arch: Путь к результирующему TAR.GZ архиву
        :raises FileNotFoundError: Если каталог‑источник не существует
        :raises NotADirectoryError: Если источник не является каталогом
        :raises OSError: Прочие ошибки файловой системы
        """
        ...

    @abstractmethod
    def untar(self, path_archive_tar_gz: PathLike[str] | str, res: PathLike[str] | str | None = None) -> None:
        """
        Абстрактный метод для распаковки TAR.GZ архива.

        :param path_archive_tar_gz: Путь к TAR.GZ архиву
        :param res: Папка назначения; если None — используется текущая рабочая директория
        :raises FileNotFoundError: Если архив не существует
        :raises OSError: Прочие ошибки файловой системы
        """
        ...

    @abstractmethod
    def grep(self, pattern: str, path: PathLike[str] | str, r: bool, ignore_case: bool) -> list[str]:
        """
        Абстрактный метод для поиска строк по регулярному выражению в файлах.

        :param pattern: Регулярное выражение для поиска
        :param path: Файл или каталог, в котором вести поиск
        :param r: Рекурсивный обход подкаталогов, если указан каталог
        :param ignore_case: Поиск без учёта регистра
        :return: Список строк формата "file:line:text"
        :raises re.error: Если регулярное выражение некорректно
        :raises OSError: Прочие ошибки файловой системы
        """
        ...
