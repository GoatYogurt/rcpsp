from docplex.mp.model import Model

# Data
n_jobs = 5
durations = [3, 2, 4, 2, 1]
resource_demands = [ [2, 1, 3, 2, 1] ]  # single resource
capacity = [4]
precedence = [(0, 2), (1, 3), (2, 4)]

# Time horizon
H = sum(durations)

# Model
mdl = Model("RCPSP")

# Start time variables
S = mdl.integer_var_list(n_jobs, lb=0, ub=H, name="S")

# Makespan
C_max = mdl.integer_var(name="C_max")
mdl.add_constraints(C_max >= S[i] + durations[i] for i in range(n_jobs))
mdl.minimize(C_max)

# Precedence constraints
for (i, j) in precedence:
    mdl.add_constraint(S[j] >= S[i] + durations[i])

# Resource constraints using time-indexed binary variables
y = {}  # y[i, t] = 1 if job i is active at time t
for i in range(n_jobs):
    for t in range(H):
        y[i, t] = mdl.binary_var(name=f"y_{i}_{t}")

        # Big-M constraints to enforce: y[i, t] = 1 → t in [S[i], S[i] + d[i] - 1]
        M = H
        mdl.add_constraint(S[i] <= t + (1 - y[i, t]) * M)
        mdl.add_constraint(S[i] + durations[i] - 1 >= t - (1 - y[i, t]) * M)

# Capacity constraint at each time point
for t in range(H):
    mdl.add_constraint(
        mdl.sum(resource_demands[0][i] * y[i, t] for i in range(n_jobs)) <= capacity[0]
    )

# Solve
solution = mdl.solve(log_output=True)

# Output
if solution:
    for i in range(n_jobs):
        print(f"Job {i}: Start at {S[i].solution_value}")
    print("Makespan:", C_max.solution_value)
    print(mdl.solve_details.status)
else:
    print("No solution found.")