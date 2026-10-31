def calculate_tat(arrival_time, completion_time):
    """Return turnaround time: completion time minus arrival time."""
    return completion_time - arrival_time


def calculate_wt(turnaround_time, burst_time):
    """Return waiting time: turnaround time minus CPU burst time."""
    return turnaround_time - burst_time


def calculate_rt(first_execution_time, arrival_time):
    """Return response time: first CPU start minus arrival time."""
    return first_execution_time - arrival_time


def calculate_throughput(completed_processes, total_time):
    """Return completed processes per unit of elapsed simulation time."""
    if total_time <= 0:
        return 0
    return completed_processes / total_time


def calculate_cpu_utilization(total_time, idle_time):
    """Return the percentage of elapsed time during which the CPU was busy."""
    if total_time <= 0:
        return 0
    return ((total_time - idle_time) / total_time) * 100


def calculate_metrics(processes, timeline):
    """Calculate per-process and overall metrics from a scheduler timeline.

    Each timeline entry must contain ``pid``, ``start_time`` and ``end_time``.
    Idle intervals use ``pid=None``. Every supplied process must receive
    exactly its declared burst time.
    """
    results = {}
    first_execution = {}
    executed_time = {}

    for process in processes:
        if process.pid in results:
            raise ValueError(f"Duplicate process ID: {process.pid}")

        results[process.pid] = {
            "arrival_time": process.arrival_time,
            "burst_time": process.burst_time,
            "completion_time": 0,
            "turnaround_time": 0,
            "waiting_time": 0,
            "response_time": 0
        }
        first_execution[process.pid] = None
        executed_time[process.pid] = 0

    for slot in timeline:
        try:
            pid = slot["pid"]
            start_time = slot["start_time"]
            end_time = slot["end_time"]
        except (KeyError, TypeError) as error:
            raise ValueError("Invalid timeline entry") from error

        if end_time <= start_time:
            raise ValueError("Timeline intervals must have positive duration")

        if pid is None:
            continue

        if pid not in results:
            raise ValueError(f"Timeline contains unknown process ID: {pid}")

        duration = end_time - start_time
        executed_time[pid] += duration

        if first_execution[pid] is None:
            first_execution[pid] = start_time

        results[pid]["completion_time"] = max(
            results[pid]["completion_time"],
            end_time
        )

    for pid, data in results.items():
        if executed_time[pid] != data["burst_time"]:
            raise ValueError(
                f"Process {pid} received {executed_time[pid]} CPU time; "
                f"expected {data['burst_time']}"
            )

        tat = calculate_tat(
            data["arrival_time"],
            data["completion_time"]
        )
        waiting = calculate_wt(tat, data["burst_time"])
        response = calculate_rt(
            first_execution[pid],
            data["arrival_time"]
        )

        if waiting < 0 or response < 0:
            raise ValueError(f"Invalid timeline for process {pid}")

        data["turnaround_time"] = tat
        data["waiting_time"] = waiting
        data["response_time"] = response

    count = len(results)

    if count:
        avg_tat = sum(
            data["turnaround_time"] for data in results.values()
        ) / count
        avg_wt = sum(
            data["waiting_time"] for data in results.values()
        ) / count
        avg_rt = sum(
            data["response_time"] for data in results.values()
        ) / count
    else:
        avg_tat = avg_wt = avg_rt = 0

    if timeline:
        start_time = min(slot["start_time"] for slot in timeline)
        end_time = max(slot["end_time"] for slot in timeline)
        total_time = end_time - start_time
        busy_time = sum(
            slot["end_time"] - slot["start_time"]
            for slot in timeline
            if slot["pid"] is not None
        )
        idle_time = total_time - busy_time
    else:
        total_time = 0
        idle_time = 0

    return {
        "process_metrics": results,
        "average_waiting_time": avg_wt,
        "average_turnaround_time": avg_tat,
        "average_response_time": avg_rt,
        "cpu_utilization": calculate_cpu_utilization(total_time, idle_time),
        "throughput": calculate_throughput(count, total_time)
    }
