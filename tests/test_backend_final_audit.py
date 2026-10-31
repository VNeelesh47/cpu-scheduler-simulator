
import pytest

from backend.process import Process
from backend.scheduler import run_scheduler, compare_algorithms


ALGORITHMS = [
    "FCFS",
    "SJF_NP",
    "SJF_P",
    "PRIORITY_NP",
    "PRIORITY_P",
    "RR"
]


@pytest.fixture
def processes():
    return [
        Process(pid="P1", arrival_time=2, burst_time=6, priority=3),
        Process(pid="P2", arrival_time=3, burst_time=2, priority=1),
        Process(pid="P3", arrival_time=5, burst_time=4, priority=2),
        Process(pid="P4", arrival_time=7, burst_time=3, priority=4),
        Process(pid="P5", arrival_time=8, burst_time=1, priority=2)
    ]


def get_original_data(processes):
    return [
        (
            p.pid,
            p.arrival_time,
            p.burst_time,
            p.priority
        )
        for p in processes
    ]


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_scheduling_invariants(processes, algorithm):

    result = run_scheduler(
        processes,
        algorithm,
        quantum=2
    )

    timeline = result["timeline"]

    execution_totals = {p.pid: 0 for p in processes}

    current_time = 0

    for slot in timeline:

        pid = slot["pid"]
        start = slot["start_time"]
        end = slot["end_time"]

        # No gaps or overlapping intervals
        assert start == current_time

        # Every interval must have positive duration
        assert end > start

        if pid is not None:

            process = next(
                p for p in processes if p.pid == pid
            )

            # Process cannot execute before arrival
            assert start >= process.arrival_time

            execution_totals[pid] += end - start

        current_time = end

    # Every process must receive exactly its burst time
    for process in processes:
        assert execution_totals[process.pid] == process.burst_time


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_metrics_independently_verified(processes, algorithm):

    result = run_scheduler(
        processes,
        algorithm,
        quantum=2
    )

    timeline = result["timeline"]
    metrics = result["metrics"]["process_metrics"]

    for process in processes:

        pid = process.pid

        execution_slots = [
            slot for slot in timeline
            if slot["pid"] == pid
        ]

        completion_time = max(
            slot["end_time"] for slot in execution_slots
        )

        first_execution = min(
            slot["start_time"] for slot in execution_slots
        )

        expected_tat = completion_time - process.arrival_time

        expected_waiting = expected_tat - process.burst_time

        expected_response = first_execution - process.arrival_time

        assert metrics[pid]["completion_time"] == completion_time

        assert metrics[pid]["turnaround_time"] == expected_tat

        assert metrics[pid]["waiting_time"] == expected_waiting

        assert metrics[pid]["response_time"] == expected_response


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_cpu_time_accounting(processes, algorithm):

    result = run_scheduler(
        processes,
        algorithm,
        quantum=2
    )

    timeline = result["timeline"]
    metrics = result["metrics"]

    total_burst_time = sum(
        p.burst_time for p in processes
    )

    total_time = timeline[-1]["end_time"]

    assert metrics["cpu_utilization"] == pytest.approx(
        (total_burst_time / total_time) * 100
    )

    assert metrics["throughput"] == pytest.approx(
        len(processes) / total_time
    )


def test_comparison_matches_individual_simulations(processes):

    comparison = compare_algorithms(
        processes,
        quantum=2
    )

    metric_names = [
        "average_waiting_time",
        "average_turnaround_time",
        "average_response_time",
        "cpu_utilization",
        "throughput"
    ]

    for algorithm in ALGORITHMS:

        individual = run_scheduler(
            processes,
            algorithm,
            quantum=2
        )["metrics"]

        for metric in metric_names:

            assert comparison[algorithm][metric] == pytest.approx(
                individual[metric]
            )


def test_algorithms_do_not_modify_process_data(processes):

    original_data = get_original_data(processes)

    for algorithm in ALGORITHMS:

        run_scheduler(
            processes,
            algorithm,
            quantum=2
        )

        assert get_original_data(processes) == original_data


def test_comparison_does_not_modify_process_data(processes):

    original_data = get_original_data(processes)

    compare_algorithms(
        processes,
        quantum=2
    )

    assert get_original_data(processes) == original_data


@pytest.mark.parametrize("algorithm", ["SJF_P", "PRIORITY_P"])
def test_preemptive_algorithms_handle_very_large_burst_efficiently(algorithm):
    processes = [
        Process(pid="P1", arrival_time=0, burst_time=1_000_000_000, priority=5),
        Process(pid="P2", arrival_time=500, burst_time=2, priority=1)
    ]

    result = run_scheduler(processes, algorithm, quantum=2)

    assert result["timeline"] == [
        {"pid": "P1", "start_time": 0, "end_time": 500},
        {"pid": "P2", "start_time": 500, "end_time": 502},
        {"pid": "P1", "start_time": 502, "end_time": 1_000_000_002}
    ]
