from backend.fcfs import fcfs_scheduling

from backend.sjf import (
    sjf_non_preemptive,
    sjf_preemptive
)

from backend.priority import (
    priority_non_preemptive,
    priority_preemptive
)

from backend.round_robin import round_robin_scheduling

from backend.metrics import calculate_metrics


def run_scheduler(processes, algorithm, quantum=None):

    if algorithm == "FCFS":
        timeline = fcfs_scheduling(processes)

    elif algorithm == "SJF_NP":
        timeline = sjf_non_preemptive(processes)

    elif algorithm == "SJF_P":
        timeline = sjf_preemptive(processes)

    elif algorithm == "PRIORITY_NP":
        timeline = priority_non_preemptive(processes)

    elif algorithm == "PRIORITY_P":
        timeline = priority_preemptive(processes)

    elif algorithm == "RR":

        if quantum is None:
            raise ValueError("Time quantum is required for Round Robin")

        timeline = round_robin_scheduling(processes, quantum)

    else:
        raise ValueError(f"Unknown scheduling algorithm: {algorithm}")

    metrics = calculate_metrics(processes, timeline)

    return {
        "algorithm": algorithm,
        "timeline": timeline,
        "metrics": metrics
    }


def compare_algorithms(processes, quantum=2):

    algorithms = {
        "FCFS": fcfs_scheduling,
        "SJF_NP": sjf_non_preemptive,
        "SJF_P": sjf_preemptive,
        "PRIORITY_NP": priority_non_preemptive,
        "PRIORITY_P": priority_preemptive,
        "RR": None
    }

    comparison = {}

    for algorithm, function in algorithms.items():

        if algorithm == "RR":
            timeline = round_robin_scheduling(processes, quantum)

        else:
            timeline = function(processes)

        metrics = calculate_metrics(processes, timeline)

        comparison[algorithm] = {
            "average_waiting_time": metrics["average_waiting_time"],
            "average_turnaround_time": metrics["average_turnaround_time"],
            "average_response_time": metrics["average_response_time"],
            "cpu_utilization": metrics["cpu_utilization"],
            "throughput": metrics["throughput"]
        }

    return comparison