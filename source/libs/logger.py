import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional, TextIO, Tuple, Union

import simplejson
from mypy.ipc import TracebackType
from pythonjsonlogger.jsonlogger import JsonFormatter

from libs.settings import settings

app_name = settings.APP_NAME
app_version = settings.APP_VERSION

logger_level = settings.LOGGER_LEVEL


NOT_CONFIGURED_TEXT = 'not_configured'
DEFAULT_EMPTY_VALUE = '-'

ENDPOINT_KEY = 'PATH_INFO'
REQUEST_PARAMS = [
    'PATH_INFO',
    'QUERY_STRING',
    'REMOTE_ADDR',
    'SERVER_NAME',
    'HTTP_REFERER',
    'HTTP_USER_AGENT',
    'REQUEST_METHOD',
]

PATH_SPLITTERS = [
    '/source/',
    '/site-packages/',
]


class ExtraLogRecord(logging.LogRecord):
    """Запись логгера, описываем дополнительные поля."""

    _extra: Dict[str, Any] = {}
    service: str
    version: str
    trace_id: str


def format_to_one_line(string: str):
    """Убирает переносы строк."""
    return string.replace('\n', '')


class CustomJsonFormatter(JsonFormatter):
    """Определение своего json форматтера."""

    _app_name = NOT_CONFIGURED_TEXT
    _app_version = NOT_CONFIGURED_TEXT
    _trace_id: Optional[Union[str, int]] = None

    def add_fields(self, log_record, record, message_dict):
        """Добавление кастомных полей."""
        if record.levelno == logging.ERROR:
            record.exc_info = sys.exc_info()
            message_dict['exc_info'] = self.formatException(record.exc_info)
        super().add_fields(log_record, record, message_dict)

        if 'extra' in log_record:
            log_record.update(log_record.pop('extra'))

        log_record['app_name'] = self._app_name
        log_record['app_version'] = self._app_version
        log_record['access_time'] = datetime.utcnow().isoformat()
        log_record['trace_id'] = self._trace_id


def get_stream_handler(stream: Optional[TextIO] = None,
                       formatter: Optional[logging.Formatter] = None) -> logging.StreamHandler:
    """Создаёт хэндлер для записи в стандартный поток.

    stream может быть sys.stderr или sys.stdout
    """
    stream_handler = logging.StreamHandler(stream=stream)
    if formatter:
        stream_handler.setFormatter(formatter)
    return stream_handler


def serializer(obj, *args, **kwargs):
    """Общая выгрузка объекта в JSON с поддержкой pydantic моделей."""
    try:
        return simplejson.dumps(obj, *args, **kwargs)
    except TypeError:
        if hasattr(obj, 'dict') and callable(obj.dict):
            return str(obj.dict())

    return str(dict(obj))


json_formatter = CustomJsonFormatter(
    json_encoder=simplejson.JSONEncoder,
    json_serializer=serializer,
)
stdout_handler = get_stream_handler(
    stream=sys.stdout,
    formatter=json_formatter,
)

enabled_handlers = [
    stdout_handler,
]


def custom_make_record(name: str,
                       level: int,
                       fn: str,
                       lno: int,
                       msg: str,
                       args: Tuple,
                       exc_info: Optional[Tuple[type, Exception, TracebackType]],
                       func: Optional[str] = None,
                       extra: Optional[Dict[str, Any]] = None,
                       sinfo: Optional[str] = None):
    """Сохраняем extra в _extra для записи в meta ELK и в rv.__dict__ для sentry.

    :param name: имя логгера
    :param level: уровень логгирования
    :param fn: это на самом деле идёт в pathname
    :param lno: номер строки
    :param msg: само сообщение логгера
    :param args: прочие параметры
    :param exc_info: информация об exception
    :param func: имя функции
    :param extra: наши экстра параметры
    :param sinfo: информация о стеке
    """
    rv = ExtraLogRecord(
        name=name,
        level=level,
        pathname=fn,
        lineno=lno,
        msg=msg,
        args=args,
        exc_info=exc_info,
        func=func,
        sinfo=sinfo,
    )
    if extra is not None:
        rv.__dict__['extra'] = extra
    rv._extra = extra or {}  # noqa: SLF001
    return rv


def init_logger_app(app_logger: logging.Logger, app_name: str, version: str):
    """Выставление значений app_name и version для дальнейшего логирования.

    :param app_logger: логгер
    :param app_name: имя сервиса
    :param version: версия сервиса
    """
    for log_handler in app_logger.handlers:
        if isinstance(log_handler.formatter, JsonFormatter):
            log_handler.formatter._app_name = app_name.replace(' ', '_').lower()  # noqa: SLF001
            log_handler.formatter._app_version = version.replace(' ', '_').lower()  # noqa: SLF001


def get_logger(name: str = 'app', level: Union[int, str] = logger_level):
    """
    Создание и настройка логгера.

    :param name: имя логгера
    :param level: уровень логгирования
    """
    _logger = logging.getLogger(name)
    for handler in enabled_handlers:
        _logger.addHandler(handler)
    _logger.setLevel(level)
    _logger.propagate = False

    _logger.makeRecord = custom_make_record  # type:ignore
    return _logger


logger = get_logger()
init_logger_app(
    app_logger=logger,
    app_name=app_name,
    version=app_version,
)