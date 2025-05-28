import unittest
import sys
import os

# Ajouter src/ au path pour importer algo.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from algo import group_students


class TestStudentGrouping(unittest.TestCase):
    def test_basic_grouping(self):
        """
        This test verifies that the group_students function correctly groups four students
        into two groups of two, maximizing the mutual affinities given in preferences.
        """
        students = [
            {"name": "Alice", "preferences": [("Bob", 10)]},
            {"name": "Bob", "preferences": [("Alice", 5)]},
            {"name": "Charlie", "preferences": [("David", 8)]},
            {"name": "David", "preferences": [("Charlie", 8)]},
        ]
        groups, group_scores, total_score = group_students(students, group_size=2)

        self.assertEqual(len(groups), 2)
        self.assertTrue(all(len(group) == 2 for group in groups))
        self.assertEqual(total_score, 31)

    def test_group_size_not_divisible(self):
        """
        This test verifies that the function correctly handles cases where the number of students
        is not divisible by the group size.
        """
        students = [
            {"name": "Alice", "preferences": [("Bob", 4)]},
            {"name": "Bob", "preferences": [("Alice", 4)]},
            {"name": "Charlie", "preferences": [("David", 4)]},
            {"name": "David", "preferences": [("Charlie", 4)]},
            {"name": "Eve", "preferences": [("Alice", 2)]},
        ]
        groups, group_scores, total_score = group_students(students, group_size=2)

        self.assertEqual(len(groups), 3)
        sizes = [len(g) for g in groups]
        self.assertTrue(sorted(sizes) in ([1, 2, 2], [2, 2, 1]))
        self.assertIsInstance(total_score, int)


    def test_no_preferences(self):
        """
        This test verifies that the program works even if no student gives a preference.
        The total score should then be 0.
        """
        students = [
            {"name": "Alice", "preferences": []},
            {"name": "Bob", "preferences": []},
            {"name": "Charlie", "preferences": []},
            {"name": "David", "preferences": []},
        ]
        groups, group_scores, total_score = group_students(students, group_size=2)

        self.assertEqual(total_score, 0)
        self.assertEqual(len(groups), 2)
        self.assertTrue(all(len(group) == 2 for group in groups))
        
if __name__ == "__main__":
    unittest.main()