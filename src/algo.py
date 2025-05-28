import json
import math
from ortools.sat.python import cp_model
import os


def load_students_from_file(file_path):
    # Load the student data from a JSON file
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def group_students(students, group_size):
    # Main function to group students using constraint programming
    model = cp_model.CpModel()
    n = len(students)
    num_groups = math.ceil(n / group_size)

    names = [s["name"] for s in students]
    name_to_idx = {name: i for i, name in enumerate(names)} # Determine how many groups are needed

    # Create assignment variables: x[i, g] is True if student i is assigned to group g
    x = {}
    for i in range(n):
        for g in range(num_groups):
            x[i, g] = model.NewBoolVar(f"x_{i}_{g}")

    # Constraint: each student must be assigned to exactly one group
    for i in range(n):
        model.Add(sum(x[i, g] for g in range(num_groups)) == 1)

    # Constraint: each group must have an appropriate number of students
    base_size = n // num_groups
    remainder = n % num_groups
    for g in range(num_groups):
        min_size = base_size + (1 if g < remainder else 0)
        model.Add(sum(x[i, g] for i in range(n)) == min_size)

    # Build preference score matrix from student preferences
    score = [[0] * n for _ in range(n)]
    for student in students:
        i = name_to_idx[student["name"]]
        for pref_name, weight in student.get("preferences", []):
            if pref_name in name_to_idx:
                j = name_to_idx[pref_name]
                if i != j:
                    score[i][j] = weight

    # Objective: maximize total mutual preference scores within each group
    objective_terms = []
    for g in range(num_groups):
        for i in range(n):
            for j in range(i + 1, n):
                same_group = model.NewBoolVar(f"samegroup_{i}_{j}_g{g}")
                model.AddBoolAnd([x[i, g], x[j, g]]).OnlyEnforceIf(same_group)
                model.AddBoolOr([x[i, g].Not(), x[j, g].Not()]).OnlyEnforceIf(same_group.Not())

                mutual_score = score[i][j] + score[j][i]
                if mutual_score > 0:
                    objective_terms.append(mutual_score * same_group)

    model.Maximize(sum(objective_terms))

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        groups = [[] for _ in range(num_groups)]
        assigned = set()

        # Retrieve group assignments from the solver
        for i in range(n):
            for g in range(num_groups):
                if solver.Value(x[i, g]):
                    groups[g].append(names[i])
                    assigned.add(i)

        # Compute the satisfaction score for each group
        group_scores = []
        total_score = 0
        for g, group in enumerate(groups):
            group_score = 0
            for i_idx in range(len(group)):
                i = name_to_idx[group[i_idx]]
                for j_idx in range(i_idx + 1, len(group)):
                    j = name_to_idx[group[j_idx]]
                    group_score += score[i][j] + score[j][i]
            group_scores.append(group_score)
            total_score += group_score

        print(f"\nSolution trouvée avec score total = {total_score}\n")
        for gi, grp in enumerate(groups):
            print(f"Groupe {gi+1} ({len(grp)} élèves) : {grp} — score = {group_scores[gi]}")
        return groups, group_scores, total_score
    else:
        print("Pas de solution trouvée.")
        return None, None, None


def save_groups(groups, group_scores):
    # Save generated groups and their scores into a JSON file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.abspath(os.path.join(base_dir, "../data/group.json"))
    
    # Prepare the data structure to save
    groups_with_scores = []
    for grp, score in zip(groups, group_scores):
        groups_with_scores.append({
            "groupe": grp,
            "score": score
        })
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(groups_with_scores, f, ensure_ascii=False, indent=2)



# Entry point of the script when run as main
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(base_dir, "../data/choice.json"))

    if not os.path.isfile(file_path):
        print(f"Fichier non trouvé : {file_path}")
        exit(1)

    # Load student data and execute the grouping logic
    students = load_students_from_file(file_path)
    print(f"{len(students)} étudiants chargés.")

    group_size = 4  # Group size parameter (can be adjusted)

    groups, group_scores= group_students(students, group_size)
    save_groups(groups, group_scores)
