
import pytest

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def valid_processes():
    return [
        {
            "pid": "P1",
            "arrival_time": 0,
            "burst_time": 5,
            "priority": 2
        },
        {
            "pid": "P2",
            "arrival_time": 1,
            "burst_time": 3,
            "priority": 1
        }
    ]


def test_invalid_algorithm():

    response = client.post(
        "/simulate",
        json={
            "processes": valid_processes(),
            "algorithm": "INVALID"
        }
    )

    assert response.status_code == 422


def test_missing_algorithm():

    response = client.post(
        "/simulate",
        json={
            "processes": valid_processes()
        }
    )

    assert response.status_code == 422


def test_negative_arrival_time():

    processes = valid_processes()
    processes[0]["arrival_time"] = -1

    response = client.post(
        "/simulate",
        json={
            "processes": processes,
            "algorithm": "FCFS"
        }
    )

    assert response.status_code == 422


def test_zero_burst_time():

    processes = valid_processes()
    processes[0]["burst_time"] = 0

    response = client.post(
        "/simulate",
        json={
            "processes": processes,
            "algorithm": "FCFS"
        }
    )

    assert response.status_code == 422


def test_missing_process_id():

    processes = valid_processes()
    del processes[0]["pid"]

    response = client.post(
        "/simulate",
        json={
            "processes": processes,
            "algorithm": "FCFS"
        }
    )

    assert response.status_code == 422


def test_compare_empty_processes():

    response = client.post(
        "/compare",
        json={
            "processes": [],
            "quantum": 2
        }
    )

    assert response.status_code == 400


def test_compare_duplicate_process_ids():

    processes = valid_processes()
    processes[1]["pid"] = "P1"

    response = client.post(
        "/compare",
        json={
            "processes": processes,
            "quantum": 2
        }
    )

    assert response.status_code == 400


def test_compare_zero_quantum():

    response = client.post(
        "/compare",
        json={
            "processes": valid_processes(),
            "quantum": 0
        }
    )

    assert response.status_code == 422


def test_compare_missing_processes():

    response = client.post(
        "/compare",
        json={
            "quantum": 2
        }
    )

    assert response.status_code == 422


def test_compare_valid_request():

    response = client.post(
        "/compare",
        json={
            "processes": valid_processes(),
            "quantum": 2
        }
    )

    assert response.status_code == 200

    expected_algorithms = {
        "FCFS",
        "SJF_NP",
        "SJF_P",
        "PRIORITY_NP",
        "PRIORITY_P",
        "RR"
    }

    assert set(response.json().keys()) == expected_algorithms


def test_empty_process_id_is_rejected():
    processes = valid_processes()
    processes[0]["pid"] = ""

    response = client.post(
        "/simulate",
        json={"processes": processes, "algorithm": "FCFS"}
    )

    assert response.status_code == 422


def test_whitespace_process_id_is_rejected():
    processes = valid_processes()
    processes[0]["pid"] = "   "

    response = client.post(
        "/simulate",
        json={"processes": processes, "algorithm": "FCFS"}
    )

    assert response.status_code == 422


def test_process_id_whitespace_is_trimmed():
    processes = valid_processes()
    processes[0]["pid"] = "  P1  "

    response = client.post(
        "/simulate",
        json={"processes": processes, "algorithm": "FCFS"}
    )

    assert response.status_code == 200
    assert "P1" in response.json()["metrics"]["process_metrics"]


def test_unknown_process_field_is_rejected():
    processes = valid_processes()
    processes[0]["remaining_time"] = 3

    response = client.post(
        "/simulate",
        json={"processes": processes, "algorithm": "FCFS"}
    )

    assert response.status_code == 422


def test_cors_preflight_for_vite_origin():
    response = client.options(
        "/simulate",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_duplicate_ids_after_whitespace_normalization_are_rejected():
    processes = valid_processes()
    processes[1]["pid"] = "  P1  "

    response = client.post(
        "/simulate",
        json={"processes": processes, "algorithm": "FCFS"}
    )

    assert response.status_code == 400


def test_compare_uses_default_quantum_when_omitted():
    response = client.post(
        "/compare",
        json={"processes": valid_processes()}
    )

    assert response.status_code == 200
    assert "RR" in response.json()


def test_cors_rejects_unconfigured_origin():
    response = client.options(
        "/simulate",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST"
        }
    )

    assert "access-control-allow-origin" not in response.headers
