import json
import math
from ortools.sat.python import cp_model
import os



def load_students_from_file(file_path):
    # Load student records from a JSON file at the specified path.
    with open(file_path, "r", encoding="utf-8") as f:
        students = json.load(f)
    return students

def group_students(students, group_size, num_preferences):
    # Create the CP-SAT model for assigning students to groups.
    model = cp_model.CpModel()

    n = len(students)
    num_groups = math.ceil(n / group_size)

    names = [s["name"] for s in students]
    name_to_idx = {name: i for i, name in enumerate(names)}
    
    # Define boolean variables x[i, g] = 1 if student i is assigned to group g.
    x = {}
    for i in range(n):
        for g in range(num_groups):
            x[i, g] = model.NewBoolVar(f'x_{i}_{g}')

    # Each student must be assigned to exactly one group.
    for i in range(n):
        model.Add(sum(x[i, g] for g in range(num_groups)) == 1)

    # Enforce group size constraints, distributing remainder evenly.
    base_size = n // num_groups
    remainder = n % num_groups
    for g in range(num_groups):
        min_size = base_size + (1 if g < remainder else 0)
        model.Add(sum(x[i, g] for i in range(n)) == min_size)

    # Compute weighted preference scores for each student pair,
    # but first filter out any deleted students and re-index the ranks.
    pref_points = list(range(num_preferences, 0, -1))
    score = [[0]*n for _ in range(n)]

    for i, student in enumerate(students):

        raw_prefs   = student.get("preferences", [])
        valid_prefs = [p for p in raw_prefs if p in name_to_idx]

        prefs = valid_prefs[:num_preferences]

        for rank, p_name in enumerate(prefs):
            j = name_to_idx[p_name]
            if j != i:
                score[i][j] += pref_points[rank]

    # Build the objective: maximize mutual affinities within groups.
    objective_terms = []
    for g in range(num_groups):
        for i in range(n):
            for j in range(i+1, n):
                same_group_ij = model.NewBoolVar(f'samegroup_{i}_{j}_g{g}')
                model.AddBoolAnd([x[i, g], x[j, g]]).OnlyEnforceIf(same_group_ij)
                model.AddBoolOr([x[i, g].Not(), x[j, g].Not()]).OnlyEnforceIf(same_group_ij.Not())

                weight = score[i][j] + score[j][i]
                if weight > 0:
                    objective_terms.append(weight * same_group_ij)

    model.Maximize(sum(objective_terms))

    # Solve the model and extract group assignments if feasible.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        groups = [[] for _ in range(num_groups)]
        assigned = set()

        for i in range(n):
            for g in range(num_groups):
                if solver.Value(x[i, g]) == 1:
                    if i in assigned:
                        print(f"Error: student {names[i]} is already assigned to a group.")
                    groups[g].append(names[i])
                    assigned.add(i)

        print(f"Solution found with total score = {solver.ObjectiveValue()}")

        for gi, grp in enumerate(groups):
            print(f"Group {gi+1} ({len(grp)} students) : {grp}")
        return groups
    else:
        print("No solution found with this group size.")
        return None
    

def save_groups(groups):
    # Save the generated groups list to the JSON file at ../data/group.json.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.abspath(os.path.join(base_dir, "../data/group.json"))
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)



if __name__ == "__main__":
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(base_dir, "../data/choice.json"))

    if not os.path.isfile(file_path):
        print(f"Error: file not found: {file_path}")
        exit(1)

    students = load_students_from_file(file_path)
    print(f"{len(students)} students loaded.")

    group_size = 4
    num_preferences = 3

    groups = group_students(students, group_size, num_preferences)
    if groups is not None:
        save_groups(groups)
