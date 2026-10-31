from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_home_endpoint():

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "CPU Scheduling Simulator API is running"
    }


def test_fcfs_simulation():

    response = client.post(
        "/simulate",
        json={
            "processes": [
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
            ],
            "algorithm": "FCFS"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["algorithm"] == "FCFS"
    assert len(data["timeline"]) == 2
    assert "metrics" in data


def test_round_robin_simulation():

    response = client.post(
        "/simulate",
        json={
            "processes": [
                {
                    "pid": "P1",
                    "arrival_time": 0,
                    "burst_time": 5
                },
                {
                    "pid": "P2",
                    "arrival_time": 1,
                    "burst_time": 3
                }
            ],
            "algorithm": "RR",
            "quantum": 2
        }
    )

    assert response.status_code == 200
    assert response.json()["algorithm"] == "RR"


def test_missing_quantum():

    response = client.post(
        "/simulate",
        json={
            "processes": [
                {
                    "pid": "P1",
                    "arrival_time": 0,
                    "burst_time": 5
                }
            ],
            "algorithm": "RR"
        }
    )

    assert response.status_code == 400


def test_empty_process_list():

    response = client.post(
        "/simulate",
        json={
            "processes": [],
            "algorithm": "FCFS"
        }
    )

    assert response.status_code == 400


def test_duplicate_process_ids():

    response = client.post(
        "/simulate",
        json={
            "processes": [
                {
                    "pid": "P1",
                    "arrival_time": 0,
                    "burst_time": 5
                },
                {
                    "pid": "P1",
                    "arrival_time": 1,
                    "burst_time": 3
                }
            ],
            "algorithm": "FCFS"
        }
    )

    assert response.status_code == 400


def test_invalid_burst_time():

    response = client.post(
        "/simulate",
        json={
            "processes": [
                {
                    "pid": "P1",
                    "arrival_time": 0,
                    "burst_time": 0
                }
            ],
            "algorithm": "FCFS"
        }
    )

    assert response.status_code == 422