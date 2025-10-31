LOGGING_CONFIG = {
    "version": 1,


    "disable_existing_loggers": False,


    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",

            "formatter": "standard",

            "level": "DEBUG",
        },

        "file": {
            "class": "logging.handlers.RotatingFileHandler",

            "formatter": "standard",

            "mode": "a",

            "filename": "shell.log",

            "encoding": "utf-8",

            "maxBytes": 5 * 1024 * 1024,

            "backupCount": 5,

            "level": "DEBUG",
        },
    },

    "loggers": {
        "": {
            "handlers": ["console", "file"],

            "level": "DEBUG",

            "propagate": True,
        }
    },
}
