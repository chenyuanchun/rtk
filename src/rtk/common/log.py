import logging
import sys


def with_logger(cls):
    """
    class decorator
    Add a logger to class
    """
    _logger_name = '.'.join((cls.__module__, cls.__name__)) if cls.__module__ else cls.__qualname__
    cls.logger = logging.getLogger(_logger_name)
    return cls


DEFAULT_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "brief": {"format": "%(levelname)-8s: %(name)-15s: %(message)s"},
        "precise": {"format": "%(asctime)s:%(levelname)s[%(name)s] %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "brief",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "precise",
            "filename": "application.log",
            "maxBytes": 1000000,
            "backupCount": 3
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": 'INFO'
    }
}


def _basic():
    """
    >>> _basic()
    INFO:log:Records: {'name': 'ray'}

    :return:
    """
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    # only the first basicConfig() call takes effect, if it's called multiple times

    logger = logging.getLogger(__name__)
    # logger.level = logging.WARNING
    logger.info('Records: %s', {'name': 'ray'})


if __name__ == '__main__':
    import doctest
    doctest.testmod()
