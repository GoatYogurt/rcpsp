import re

def parse_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    jobs = {}
    resource_availability = []
    n_jobs = 0
    parsing_precedence = False
    parsing_requests = False
    parsing_resources = False

    for line in lines:
        line = line.strip()
        
        # Detect job count and horizon
        if "jobs" in line and ":" in line:
            n_jobs = int(re.findall(r"\d+", line)[0])

        # --- PRECEDENCE ---
        if "PRECEDENCE RELATIONS" in line:
            parsing_precedence = True
            continue
        if parsing_precedence and line.startswith("***"):
            parsing_precedence = False
            continue
        if parsing_precedence and re.match(r"\d+", line):
            parts = list(map(int, line.split()))
            job_id, _, n_successors = parts[:3]
            successors = parts[3:]
            jobs[job_id] = {'successors': successors}

        # --- REQUESTS/DURATIONS ---
        if "REQUESTS/DURATIONS" in line:
            parsing_requests = True
            continue
        if parsing_requests and line.startswith("----"):
            continue
        if parsing_requests and line.startswith("***"):
            parsing_requests = False
            continue
        if parsing_requests and re.match(r"\d+", line):
            parts = list(map(int, line.split()))
            job_id, mode, duration = parts[:3]
            resource_usage = parts[3:]
            if job_id not in jobs:
                jobs[job_id] = {}
            jobs[job_id].update({'duration': duration, 'resources': resource_usage})

        # --- RESOURCE AVAILABILITIES ---
        if "RESOURCEAVAILABILITIES" in line:
            parsing_resources = True
            continue
        if parsing_resources and re.match(r"\d", line):
            resource_availability = list(map(int, line.split()))
            parsing_resources = False

    return {
        'n_jobs': n_jobs,
        'jobs': jobs,
        'resource_availability': resource_availability
    }