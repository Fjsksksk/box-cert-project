import sys
import os
import json
import math
import pytest

# Add the src/ directory to the Python path so we can import algo.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, ROOT)

from algo import load_students_from_file, group_students



def test_load_students_from_file_reads_and_returns_expected_records(tmp_path):
    """
    Test that load_students_from_file correctly loads student records
    from a JSON file and returns the exact data structure.
    """
    # Arrange
    sample_data = [
        {"name": "Alice", "preferences": ["Bob"]},
        {"name": "Bob",   "preferences": ["Alice"]}
    ]
    json_file = tmp_path / "students.json"
    json_file.write_text(json.dumps(sample_data, ensure_ascii=False))

    # Act
    result = load_students_from_file(str(json_file))

    # Assert
    assert result == sample_data, "Loaded data did not match the expected student records."
    print("Passed: load_students_from_file returns correct data structure.")



def test_group_students_creates_correct_group_sizes_and_no_duplicates():
    """
    Ensure group_students produces the right number of groups with the correct sizes
    (including distributing remainder evenly) and that each student appears exactly once.
    """
    # Arrange
    students = [
        {"name": "A", "preferences": []},
        {"name": "B", "preferences": []},
        {"name": "C", "preferences": []}
    ]

    # Act
    groups = group_students(students, group_size=2, num_preferences=0)

    # Assert
    sizes = sorted(len(g) for g in groups)
    assert sizes == [1, 2], f"Expected group sizes [1, 2], got {sizes}"
    flat_list = [student for group in groups for student in group]
    assert set(flat_list) == {"A", "B", "C"}, "Some students are missing or duplicated across groups."
    assert len(flat_list) == 3, "Total number of assigned students should equal number of input students."
    print("Passed: group_students respects size distribution and uniqueness of assignment.")


def test_group_students_honors_mutual_affinity_priority():
    """
    Verify that students with mutual preference appear in the same group
    when num_preferences is set to include that preference.
    """
    # Arrange
    students = [
        {"name": "A", "preferences": ["B"]},
        {"name": "B", "preferences": ["A"]},
        {"name": "C", "preferences": []},
        {"name": "D", "preferences": []},
    ]

    # Act
    groups = group_students(students, group_size=2, num_preferences=1)

    # Assert
    assert any({"A", "B"}.issubset(set(group)) for group in groups), \
        "Expected A and B (mutual preference) to be grouped together."
    print("Passed: group_students groups mutual-affinity students together.")
