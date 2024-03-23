# Example gunicorn config
import json

wsgi_app = "tests:app"
accesslog = "-"
access_log_format = json.dumps(
    {
        # https://docs.gunicorn.org/en/stable/settings.html#access-log-format
        "message": "%(r)s",
        "remote_address": "%(h)s",
        "user_name": "%(u)s",
        "request_date": "%(t)s",
        "status_line": "%(r)s",
        "request_method": "%(m)s",
        "request_url": "%(U)s",
        "query_string": "%(q)s",
        "protocol": "%(H)s",
        "status": "%(s)s",
        "response_length": "%(B)s",
        "response_length_or-clf_format": "%(b)s",
        "referer": "%(f)s",
        "user_agent": "%(a)s",
        "request_seconds": "%(T)s",
        "request_miliseconds": "%(M)s",
        "request_microseconds": "%(D)s",
        "request_decimal_seconds": "%(L)s",
        "process_id": "%(p)s",
        # Request Headers (i)
        "REQUEST_HEADER": "%({accept}i)s",
        # Response Headers (o)
        "RESPONSE_HEADER": "%({content-type}o)s",
        # Environment Variable (e)
        "ENVIRONMENT_VARIABLE": "%({server_software}e)s",
    }
)
errorlog = "-"
loglevel = "debug"
logger_class = "gunicorn_json_logger.jsonlogger.Logger"
logconfig_dict = {
    "version": 1,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(levelname)s %(message)s %(pathname)s %(lineno)d %(name)s %(process)d",
            # Any arguments that the pythonjsonlogger.jsonlogger.JsonFormatter constructor takes
            # may be passed in to a formatter.
            "json_indent": 4,
            "timestamp": True,
        },
        "json_access": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(levelname)s %(message)s %(name)s %(process)d",
            "json_indent": 4,
            "timestamp": True,
        },
    },
    "handlers": {
        "json": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "json_access": {
            "class": "logging.StreamHandler",
            "formatter": "json_access",
            "stream": "ext://sys.stdout",
        },
        "json_error": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "gunicorn.access": {
            "level": "INFO",
            "propagate": False,
            "handlers": ["json_access"],
        },
        "gunicorn.error": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["json_error"],
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["json"],
    },
    "incremental": False,
    "disable_existing_loggers": False,
}
