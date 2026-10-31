def fcfs_scheduling(processes):
    # Sort processes by arrival time
    processes = sorted(
        processes,
        key=lambda p: p.arrival_time
    )

    timeline = []
    current_time = 0

    for process in processes:

        # Handle CPU idle time
        if current_time < process.arrival_time:
            timeline.append({
                "pid": None,
                "start_time": current_time,
                "end_time": process.arrival_time
            })

            current_time = process.arrival_time

        # Execute process
        start_time = current_time
        end_time = start_time + process.burst_time

        timeline.append({
            "pid": process.pid,
            "start_time": start_time,
            "end_time": end_time
        })

        current_time = end_time

    return timeline