# Импорт класса Logger для работы с логированием
from logging import Logger
# Импорт типов PathLike и функции stat из модуля os
from os import PathLike
# Импорт класса Path для работы с путями файловой системы
from pathlib import Path
import shutil
# Импорт модуля stat с псевдонимом для работы с правами доступа
import stat as stat_module
# Импорт класса datetime для работы с датами и временем
from datetime import datetime

# Импорт перечислений для режимов чтения файлов и отображения
from src.enums import FileReadMode, FileDisplayMode
# Импорт базового класса для сервисов консоли
from src.services.base import OSConsoleServiceBase


class WindowsConsoleService(OSConsoleServiceBase):
    """
    Сервис для работы с консолью в операционной системе Windows.
    Реализует методы для отображения содержимого директорий и файлов.
    """

    def __init__(self, logger: Logger):
        """
        Инициализация сервиса консоли Windows.

        :param logger: Логгер для записи информации о работе сервиса
        """
        # Сохраняем логгер для использования в методах класса
        self._logger = logger


    def format_detailed(self, entry: Path) -> str:
        """
        Вспомогательный метод для форматирования подробной информации о файле или директории.
        Создает строку с информацией о типе, правах доступа, размере, дате изменения и имени.

        :param entry: Объект Path, представляющий файл или директорию
        :return: Отформатированная строка с подробной информацией
        """
        try:
            # Получаем статистическую информацию о файле/директории
            stat_info = entry.stat()

            # Получаем права доступа в числовом формате (octal)
            mode = oct(stat_module.S_IMODE(stat_info.st_mode))[2:]
            permissions = mode

            # Получаем размер файла в байтах
            size = stat_info.st_size

            # Получаем время последнего изменения и форматируем его
            mtime = datetime.fromtimestamp(stat_info.st_mtime)
            mtime_pretty = mtime.strftime("%Y-%m-%d %H:%M:%S")

            # Определяем тип элемента: 'd' для директории, '-' для файла
            if entry.is_dir():
                entry_type = "d"
            else:
                entry_type = "-"
            # Форматируем строку с выравниванием размера по правому краю
            formatted_line = f"{entry_type}{permissions} {size:>10} {mtime_pretty} {entry.name}\n"

            # Возвращаем отформатированную строку
            return formatted_line

        except OSError as e:
            # Логируем предупреждение о невозможности получить детальную информацию
            self._logger.warning(f"Could not get detailed info for {entry}: {e}")
            # Возвращаем строку с заглушками для недоступной информации
            return f"? ? ? ? {entry.name}\n"

    def ls(self, path: PathLike[str] | str, display_mode: FileDisplayMode = FileDisplayMode.simple) -> list[str]:
        """
        Метод для отображения содержимого директории.
        Поддерживает простой и подробный режимы отображения.

        :param path: Путь к директории для отображения
        :param display_mode: Режим отображения (простой или подробный)
        :return: Список строк с информацией о файлах и директориях
        :raises FileNotFoundError: Если директория не найдена
        :raises NotADirectoryError: Если указанный путь не является директорией
        """
        # Преобразуем путь в объект Path для удобной работы
        # Исправление для поддержки Typer ArgumentInfo
        if hasattr(path, 'value'):
            path = path.value
        path = Path(path)
        # Проверяем существование пути
        if not path.exists():
            # Логируем ошибку о том, что директория не найдена
            self._logger.error(f"Folder not found: {path}")
            # Выбрасываем исключение FileNotFoundError
            raise FileNotFoundError(path)
        # Проверяем, что путь является директорией
        if not path.is_dir():
            # Логируем ошибку о том, что путь не является директорией
            self._logger.error(f"You entered {path} is not a directory")
            # Выбрасываем исключение NotADirectoryError
            raise NotADirectoryError(path)

        # Логируем информацию о начале отображения директории
        self._logger.info(f"Listing {path} in {display_mode} mode")

        # Получаем список всех элементов в директории
        entries = list(path.iterdir())
        # Сортируем элементы: сначала директории, потом файлы, в алфавитном порядке
        entries.sort(key=lambda x: (x.is_file(), x.name.lower()))

        # Проверяем режим отображения
        if display_mode == FileDisplayMode.simple:
            # Возвращаем простой список имен файлов с переносами строк
            return [entry.name + "\n" for entry in entries]
        else:
            # Возвращаем подробную информацию о каждом элементе
            return [self.format_detailed(entry) for entry in entries]




    def cat(self, file: PathLike[str] | str, mode: FileReadMode = FileReadMode.string)->str | bytes:
        """
        Метод для чтения и отображения содержимого файла.

        ЧТО ДЕЛАЕТ:
        - Читает содержимое файла и возвращает его
        - Поддерживает текстовый и бинарный режимы чтения
        - Работает с относительными и абсолютными путями
        - Логирует все операции и ошибки в файл shell.log

        ТРЕБОВАНИЯ:
        - Запрещено использовать subprocess и системные команды
        - Все операции выполняются через Python API (pathlib)
        - Проверяет, что путь существует
        - Проверяет, что путь указывает на файл (не директорию)
        - Подробное логирование всех операций

        :param file: Путь к файлу для чтения (может быть относительным или абсолютным)
        :param mode: Режим чтения файла (FileReadMode.string или FileReadMode.bytes)
        :return: Содержимое файла в виде строки или байтов
        :raises FileNotFoundError: Если файл не найден
        :raises IsADirectoryError: Если указанный путь является директорией
        :raises OSError: При ошибках чтения файла
        """
        # ============================================
        # ШАГ 1: Преобразование пути в объект Path
        # ============================================
        # Path() - универсальный способ работы с путями в Python
        # Автоматически обрабатывает относительные и абсолютные пути
        # Пример: "file.txt", "./file.txt", "C:/Users/file.txt"
        path = Path(file)

        # Логируем начало операции чтения файла
        # INFO - уровень для информационных сообщений
        self._logger.info(f"cat: Starting to read file '{file}' in mode {mode}")

        # ============================================
        # ШАГ 2: Проверка существования файла
        # ============================================
        # path.exists() - проверяет существование файла/папки
        # follow_symlinks=True - следует по символическим ссылкам
        # Если файл не существует, создаем ошибку
        if not path.exists(follow_symlinks=True):
            # Логируем ошибку с уровнем ERROR
            # Это серьезная ошибка - файл не найден
            error_msg = f"cat: File not found: '{file}' (path does not exist)"
            self._logger.error(error_msg)

            # Выбрасываем исключение FileNotFoundError
            # Это стандартное исключение Python для отсутствующих файлов
            raise FileNotFoundError(error_msg)

        # ============================================
        # ШАГ 3: Проверка, что это файл, а не папка
        # ============================================
        # path.is_dir() - проверяет, является ли путь директорией
        # Если это директория, мы не можем прочитать ее содержимое через cat
        if path.is_dir(follow_symlinks=True):
            # Логируем ошибку: передана директория вместо файла
            error_msg = f"cat: Path is a directory, not a file: '{file}'"
            self._logger.error(error_msg)

            # Выбрасываем исключение IsADirectoryError
            # Это специальное исключение для случая "ожидали файл, получили папку"
            raise IsADirectoryError(error_msg)

        # ============================================
        # ШАГ 4: Чтение файла
        # ============================================
        # Используем try-except для обработки возможных ошибок чтения
        # Могут быть ошибки: нет прав на чтение, файл используется другой программой и т.д.
        try:
            # Проверяем режим чтения файла
            if mode == FileReadMode.string:
                # ==========================================
                # Режим чтения как ТЕКСТ
                # ==========================================
                # path.read_text() - читает файл как текст (строку)
                # encoding="utf-8" - используем кодировку UTF-8 (поддерживает русские буквы)
                # Это метод Python API - НЕ используем subprocess!

                self._logger.debug(f"cat: Reading file '{file}' as text (UTF-8)")
                file_content = path.read_text(encoding="utf-8")

                # Логируем успешное чтение
                self._logger.info(f"cat: Successfully read file '{file}' as text ({len(file_content)} characters)")

                # Возвращаем содержимое файла
                return file_content

            elif mode == FileReadMode.bytes:
                # ==========================================
                # Режим чтения как БАЙТЫ
                # ==========================================
                # path.read_bytes() - читает файл как бинарные данные
                # Это нужно для изображений, исполняемых файлов и т.д.
                # Это метод Python API - НЕ используем subprocess!

                self._logger.debug(f"cat: Reading file '{file}' as bytes")
                content_bytes = path.read_bytes()

                # Логируем успешное чтение
                self._logger.info(f"cat: Successfully read file '{file}' as bytes ({len(content_bytes)} bytes)")

                # Возвращаем содержимое файла
                return content_bytes

            else:
                # Невозможная ситуация - неизвестный режим чтения
                error_msg = f"cat: Unknown read mode: {mode}"
                self._logger.error(error_msg)
                raise ValueError(error_msg)

        except OSError as e:
            # ==========================================
            # Обработка ошибок при чтении файла
            # ==========================================
            # OSError - общий класс для ошибок операционной системы
            # Может быть: нет прав, файл занят, поврежден и т.д.

            # self._logger.exception() - логирует полную информацию об ошибке
            # Включает: сообщение об ошибке, стек вызовов (traceback)
            # Это помогает отладить проблему
            self._logger.exception(f"cat: Error reading file '{file}': {e}")

            # Перебрасываем исключение выше, чтобы обработать его в main.py
            raise

    def cd(self, path: PathLike[str] | str) -> str:
        """
        Метод для перехода в указанный каталог (смена рабочей директории).

        ЧТО ДЕЛАЕТ:
        - Переходит в указанную директорию
        - Поддерживает специальные пути: . , .. , ~
        - Возвращает абсолютный путь к новой директории

        ТРЕБОВАНИЯ:
        - Запрещено использовать subprocess и системные команды
        - Все операции через Python API (pathlib, os)
        - Поддерживает относительные и абсолютные пути
        - Подробное логирование всех операций

        :param path: Путь к директории для перехода
                     . - текущая директория
                     .. - родительская директория (на уровень выше)
                     ~ - домашняя директория пользователя
        :return: Абсолютный путь к новой рабочей директории
        :raises FileNotFoundError: Если директория не существует
        :raises NotADirectoryError: Если путь не является директорией
        """
        # Импортируем os для получения домашней директории и смены рабочей директории
        import os

        # ============================================
        # ШАГ 1: Получение текущей рабочей директории
        # ============================================
        # os.getcwd() - возвращает текущую рабочую директорию процесса
        # Это абсолютный путь к папке, где запущен Python
        current_dir = Path(os.getcwd())

        # Логируем начало операции смены директории
        self._logger.info(f"cd: Attempting to change directory to '{path}'")

        # ============================================
        # ШАГ 2: Обработка специальных путей
        # ============================================

        # Преобразуем путь в строку для удобства обработки
        path_str = str(path)

        # Обработка тильды ~ (домашняя директория)
        if path_str == "~" or path_str.startswith("~/"):
            # os.path.expanduser() - преобразует ~ в путь к домашней директории
            # На Windows: C:\Users\Username
            # На Linux/Mac: /home/username
            path_str = os.path.expanduser(path_str)
            self._logger.debug(f"cd: Expanded ~ to '{path_str}'")

        # Преобразуем строку пути в объект Path
        target_path = Path(path_str)

        # ============================================
        # ШАГ 3: Обработка относительных путей
        # ============================================

        # Проверяем, является ли путь относительным (не начинается с / или C:\ на Windows)
        if not target_path.is_absolute():
            # Для относительного пути используем текущую директорию как базовую
            # Path / Path - операция объединения путей
            target_path = current_dir / target_path
            self._logger.debug(f"cd: Converted relative path to absolute: '{target_path}'")

        # ============================================
        # ШАГ 4: Получение абсолютного пути и разрешение символических ссылок
        # ============================================
        # target_path.resolve() - преобразует путь в абсолютный и разрешает символические ссылки
        # .. - преобразуется в родительскую директорию
        # . - преобразуется в текущую директорию
        target_path = target_path.resolve()
        self._logger.debug(f"cd: Resolved path to '{target_path}'")

        # ============================================
        # ШАГ 5: Проверка существования директории
        # ============================================
        if not target_path.exists():
            # Логируем ошибку: директория не существует
            error_msg = f"cd: Directory not found: '{path}' (resolved to '{target_path}')"
            self._logger.error(error_msg)

            # Выбрасываем исключение FileNotFoundError
            raise FileNotFoundError(error_msg)

        # ============================================
        # ШАГ 6: Проверка, что путь является директорией
        # ============================================
        if not target_path.is_dir():
            # Логируем ошибку: путь не является директорией
            error_msg = f"cd: Path is not a directory: '{path}' (resolved to '{target_path}')"
            self._logger.error(error_msg)

            # Выбрасываем исключение NotADirectoryError
            raise NotADirectoryError(error_msg)

        # ============================================
        # ШАГ 7: Смена рабочей директории
        # ============================================
        # os.chdir() - меняет текущую рабочую директорию процесса
        # После этого все относительные пути будут идти от этой директории
        os.chdir(target_path)

        # Получаем подтверждение новой директории

        # Логируем успешную смену директории
        self._logger.info(f"cd: Successfully changed directory to '{target_path}' (from '{current_dir}')")

        # Возвращаем новый абсолютный путь
        return str(target_path)

    def cp(self, src: PathLike[str] | str, dst: PathLike[str] | str, recursive: bool = False) -> None:
        """
        К6опирование файла или каталога.

        Поддерживает копирование в существующий каталог и рекурсивное копирование каталогов.
        """
        src_path = Path(src)
        dst_path = Path(dst)

        self._logger.info(f"cp: src='{src_path}', dst='{dst_path}', recursive={recursive}")

        if not src_path.exists():
            error_msg = f"cp: Source not found: '{src_path}'"
            self._logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            if src_path.is_dir():
                if not recursive:
                    error_msg = f"cp: '{src_path}' is a directory; use -r for recursive copy"
                    self._logger.error(error_msg)
                    raise IsADirectoryError(error_msg)

                # Определяем конечный путь каталога
                if dst_path.exists() and dst_path.is_dir():
                    final_dst = dst_path / src_path.name
                else:
                    final_dst = dst_path

                self._logger.debug(f"cp: copytree from '{src_path}' to '{final_dst}'")
                if final_dst.exists():
                    # Поведение как у cp -r: нельзя копировать в уже существующую директорию одноименно
                    # Упростим: если существует, то копируем внутрь (на уровень выше обработано),
                    # иначе бросаем исключение
                    if final_dst.is_dir():
                        # Копирование содержимого каталога внутрь существующей папки назначения
                        for child in src_path.iterdir():
                            target_child = final_dst / child.name
                            if child.is_dir():
                                shutil.copytree(child, target_child)
                            else:
                                shutil.copy2(child, target_child)
                    else:
                        raise FileExistsError(f"cp: Destination exists and is not a directory: '{final_dst}'")
                else:
                    shutil.copytree(src_path, final_dst)
            else:
                # Копирование файла
                if dst_path.exists() and dst_path.is_dir():
                    final_dst = dst_path / src_path.name
                else:
                    final_dst = dst_path

                self._logger.debug(f"cp: copy2 from '{src_path}' to '{final_dst}'")
                # Создаем родительские директории, если нужно
                final_dst_parent = final_dst.parent
                if not final_dst_parent.exists():
                    final_dst_parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, final_dst)

            self._logger.info(f"cp: Completed copy to '{dst_path}'")
        except PermissionError as e:
            self._logger.exception(f"cp: Permission denied while copying '{src_path}' -> '{dst_path}': {e}")
            raise
        except OSError as e:
            self._logger.exception(f"cp: OS error while copying '{src_path}' -> '{dst_path}': {e}")
            raise

    def mv(self, src: PathLike[str] | str, dst: PathLike[str] | str) -> None:
        """
        Перемещение/переименование файла или каталога. Поддерживает перемещение в существующий каталог.
        """
        src_path = Path(src)
        dst_path = Path(dst)

        self._logger.info(f"mv: src='{src_path}', dst='{dst_path}'")

        if not src_path.exists():
            error_msg = f"mv: Source not found: '{src_path}'"
            self._logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            final_dst: Path
            if dst_path.exists() and dst_path.is_dir():
                final_dst = dst_path / src_path.name
            else:
                final_dst = dst_path

            self._logger.debug(f"mv: moving '{src_path}' to '{final_dst}'")
            # Создаем родительские директории для назначения при необходимости
            final_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(final_dst))
            self._logger.info(f"mv: Completed move to '{final_dst}'")
        except PermissionError as e:
            self._logger.exception(f"mv: Permission denied while moving '{src_path}' -> '{dst_path}': {e}")
            raise
        except OSError as e:
            self._logger.exception(f"mv: OS error while moving '{src_path}' -> '{dst_path}': {e}")
            raise

    def rm(self, target: PathLike[str] | str, recursive: bool = False) -> None:
        """
        Удаление файла или каталога. Для каталогов требуется recursive=True.
        Ограничения: нельзя удалять корень диска и путь '..'.
        """
        path = Path(target)
        self._logger.info(f"rm: target='{path}', recursive={recursive}")

        # Запрещаем '..' явно
        path_str = str(target).strip()
        if path_str in {"..", "/"}:
            error_msg = "rm: Deleting '..' or '/' is forbidden"
            self._logger.error(error_msg)
            raise PermissionError(error_msg)

        # Разрешаем и нормализуем путь
        resolved = path.resolve()

        # Защита от удаления корня диска (C:\, D:\ и т.д.)
        if resolved == Path(resolved.anchor):
            error_msg = f"rm: Deleting root is forbidden: '{resolved}'"
            self._logger.error(error_msg)
            raise PermissionError(error_msg)

        if not resolved.exists():
            error_msg = f"rm: Path not found: '{path}'"
            self._logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            if resolved.is_dir():
                if not recursive:
                    error_msg = f"rm: '{path}' is a directory; use -r for recursive removal"
                    self._logger.error(error_msg)
                    raise IsADirectoryError(error_msg)
                self._logger.debug(f"rm: rmtree '{resolved}'")
                shutil.rmtree(resolved)
            else:
                self._logger.debug(f"rm: unlink '{resolved}'")
                resolved.unlink()

            self._logger.info(f"rm: Removed '{resolved}'")
        except PermissionError as e:
            self._logger.exception(f"rm: Permission denied while removing '{resolved}': {e}")
            raise
        except OSError as e:
            self._logger.exception(f"rm: OS error while removing '{resolved}': {e}")
            raise
