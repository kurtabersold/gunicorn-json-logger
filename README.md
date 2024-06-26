# gunicorn-json-logger

A JSON logger class for [Gunicorn](https://docs.gunicorn.org/en/stable/settings.html#logger-class) that that quacks like `gunicorn.glogging.Logger`

Powered by [python-json-logger](https://github.com/madzak/python-json-logger)

## Usage

In [`gunicorn.conf.py`](./gunicorn.conf.py), update the following:
* `accesslog` to `"-"`
* `access_log_format` to a json encoded string
* `logger_class` to `gunicorn_json_logger.jsonlogger.Logger`
* Optionally update `logconfig_dict` as shown [below](#Customization) to customer the formatter.

Example:
```python
# gunicorn.conf.py
import json

accesslog = "-"
access_log_format = json.dumps(
    {
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
logger_class = "gunicorn_json_logger.jsonlogger.Logger"
```

Refer to [Gunicorn documentation](https://docs.gunicorn.org/en/stable/settings.html) for additional settings.

## Customization
If you would like to customize the formatter, update `logconfig_dict` with  [configuration dictionary schema](https://docs.python.org/3/library/logging.config.html#logging-config-dictschema).
The primary use case is passing `pythonjsonlogger.jsonlogger.JsonFormatter` [constructor arguments](https://github.com/madzak/python-json-logger/blob/master/src/pythonjsonlogger/jsonlogger.py#L124-L144) to formatter instances.

This example adds the `json_indent` argument to pretty-prints the logs, and the `timestamp` argument to add an ISO-8601 timestamp to log messages.


```python
# gunicorn.conf.py
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
```
