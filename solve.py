from docplex.mp.model import Model
from parser import parse_file

# Load the data
data = parse_file('j30.sm\j302_1.sm')
# Job 2: {'successors': [6, 11, 15], 'duration': 8, 'resources': [4, 0, 0, 0]}


# Define the data
n_jobs = data['n_jobs']
capacity = data['resource_availability']
n_resources = len(capacity)
all_jobs = data['jobs']
durations = []
demands = []
precedence = []

for i in range(1, n_jobs + 1):
    durations.append(all_jobs[i]['duration'])
    job_successors = all_jobs[i]['successors']

    if len(job_successors) == 0:
        continue

    for successor in job_successors:
        precedence.append((i - 1, successor - 1))

for i in range(n_resources):
    resources = []
    for j in range(1, n_jobs + 1):
        resources.append(all_jobs[j]['resources'][i])
    demands.append(resources)

print(durations)
print(precedence)
print(capacity)
print(demands)


# Time horizon upper bound: sum of all durations
H = sum(durations)
print(H)

mdl = Model("RCPSP_MultiResource")

# Start time for each job
S = mdl.integer_var_list(n_jobs, lb=0, ub=H, name="S")

# Makespan variable
C_max = mdl.integer_var(name="C_max")
mdl.add_constraints(C_max >= S[i] + durations[i] for i in range(n_jobs))
mdl.minimize(C_max)

# Precedence constraints
for (i, j) in precedence:
    mdl.add_constraint(S[j] >= S[i] + durations[i])

# Time-indexed binary variables: y[i, t] = 1 if job i is active at time t
y = {}
for i in range(n_jobs):
    for t in range(H):
        y[i, t] = mdl.binary_var(name=f"y_{i}_{t}")

        # Enforce y[i,t] = 1 → t in [S[i], S[i] + d[i] - 1] using Big-M
        M = H
        mdl.add_constraint(S[i] <= t + (1 - y[i, t]) * M)
        mdl.add_constraint(S[i] + durations[i] - 1 >= t - (1 - y[i, t]) * M)

# Capacity constraints for each resource at each time step
for k in range(n_resources):
    for t in range(H):
        mdl.add_constraint(
            mdl.sum(demands[k][i] * y[i, t] for i in range(n_jobs)) <= capacity[k]
        )

# Each job must run for exactly its duration
for i in range(n_jobs):
    mdl.add_constraint(mdl.sum(y[i, t] for t in range(H)) == durations[i])

solution = mdl.solve(log_output=True)

if solution:
    for i in range(n_jobs):
        print(f"Job {i}: Start at {S[i].solution_value}")
    print("Makespan:", C_max.solution_value)
    print("Solver status:", mdl.solve_details.status)
else:
    print("No solution found.")
