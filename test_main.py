from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_history():
    """test standard history"""
    client.get("/calc?input=1-1")
    client.get("/calc?input=1-1")
    response = client.get("/history")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_history_status():
    """test history with status filter"""
    client.get("/calc?input=*-1")
    client.get("/calc?input=1-1")
    response = client.get("history/?status=fail")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_history_limit():
    """test history with status filter"""
    client.get("/calc?input=1-1")
    client.get("/calc?input=1-1")
    response = client.get("history/?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_history_err():
    """test history error"""
    client.get("/calc?input=1-1")
    client.get("/calc?input=1-1")
    response_status = client.get("/history/?status=abcd")
    limit_status = client.get("/history/?limit=400")
    assert response_status.status_code == 400
    assert limit_status.status_code == 400


def test_get_err():
    """test *9+2"""
    response = client.get("/calc?input=%2A9%2B2")
    assert response.status_code == 400


def test_get_diff():
    """test 3.2-6"""
    response = client.get("/calc?input=3.2-6")
    assert response.status_code == 200
    assert response.json()['response'] == -2.8


def test_get_mult():
    """test -2*4*4"""
    response = client.get("/calc?input=-2%2A4%2A4")
    assert response.status_code == 200
    assert response.json()['response'] == -32


def test_get_dev():
    """test 9/28"""
    response = client.get("/calc?input=9%2F28")
    assert response.status_code == 200
    assert response.json()['response'] == 0.321
