import datetime
import json
import types

import gunicorn.config
import pytest

import gunicorn_json_logger.jsonlogger

access_log_format = json.dumps(
    {
        "message": "%(r)s",
        "remote_address": "%(h)s",
        "user_name": "%(u)s",
        "request_timestamp": "%(t)s",
        "status": "%(s)s",
        "response_length": "%(b)s",
        "referer": "%(f)s",
        "user_agent": "%(a)s",
    }
)


@pytest.fixture(scope="function")
def logger():
    config = gunicorn.config.Config()
    config.set("access_log_format", access_log_format)
    logger = gunicorn_json_logger.jsonlogger.Logger(config)
    yield logger


def test_atoms_defaults(logger):
    response = types.SimpleNamespace(
        status="200",
        response_length=1024,
        headers=(("Content-Type", "application/json"),),
        sent=1024,
    )
    request = types.SimpleNamespace(headers=(("Accept", "application/json"),))
    environ = {
        "REQUEST_METHOD": "GET",
        "RAW_URI": "/my/path?foo=bar",
        "PATH_INFO": "/my/path",
        "QUERY_STRING": "foo=bar",
        "SERVER_PROTOCOL": "HTTP/1.1",
    }
    atoms = logger.atoms(response, request, environ, datetime.timedelta(seconds=1))
    assert isinstance(atoms, dict)
    assert atoms["r"] == "GET /my/path?foo=bar HTTP/1.1"
    assert atoms["m"] == "GET"
    assert atoms["U"] == "/my/path"
    assert atoms["q"] == "foo=bar"
    assert atoms["H"] == "HTTP/1.1"
    assert atoms["b"] == "1024"
    assert atoms["B"] == 1024
    assert atoms["{accept}i"] == "application/json"
    assert atoms["{content-type}o"] == "application/json"


def test_atoms_zero_bytes(logger):
    response = types.SimpleNamespace(
        status="200",
        response_length=0,
        headers=(("Content-Type", "application/json"),),
        sent=0,
    )
    request = types.SimpleNamespace(headers=(("Accept", "application/json"),))
    environ = {
        "REQUEST_METHOD": "GET",
        "RAW_URI": "/my/path?foo=bar",
        "PATH_INFO": "/my/path",
        "QUERY_STRING": "foo=bar",
        "SERVER_PROTOCOL": "HTTP/1.1",
    }
    atoms = logger.atoms(response, request, environ, datetime.timedelta(seconds=1))
    assert atoms["b"] == "0"
    assert atoms["B"] == 0


@pytest.mark.parametrize(
    "auth",
    [
        # auth type is case in-sensitive
        "Basic YnJrMHY6",
        "basic YnJrMHY6",
        "BASIC YnJrMHY6",
    ],
)
def test_get_username_from_basic_auth_header(auth, logger):
    request = types.SimpleNamespace(headers=())
    response = types.SimpleNamespace(
        status="200",
        response_length=1024,
        sent=1024,
        headers=(("Content-Type", "text/plain"),),
    )
    environ = {
        "REQUEST_METHOD": "GET",
        "RAW_URI": "/my/path?foo=bar",
        "PATH_INFO": "/my/path",
        "QUERY_STRING": "foo=bar",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "HTTP_AUTHORIZATION": auth,
    }
    atoms = logger.atoms(response, request, environ, datetime.timedelta(seconds=1))
    assert atoms["u"] == "brk0v"


def test_get_username_handles_malformed_basic_auth_header(logger):
    """Should catch a malformed auth header"""
    request = types.SimpleNamespace(headers=())
    response = types.SimpleNamespace(
        status="200",
        response_length=1024,
        sent=1024,
        headers=(("Content-Type", "text/plain"),),
    )
    environ = {
        "REQUEST_METHOD": "GET",
        "RAW_URI": "/my/path?foo=bar",
        "PATH_INFO": "/my/path",
        "QUERY_STRING": "foo=bar",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "HTTP_AUTHORIZATION": "Basic ixsTtkKzIpVTncfQjbBcnoRNoDfbnaXG",
    }

    atoms = logger.atoms(response, request, environ, datetime.timedelta(seconds=1))
    assert atoms["u"] == "-"
