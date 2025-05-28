import unittest
import sys
import os

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


    def test_unilateral_preferences(self):
        """
        Test with affinities.
        The total score must take into account all affinities.
        """
        students = [
            {"name": "Alice", "preferences": [("Bob", 10)]},
            {"name": "Bob", "preferences": []},
            {"name": "Charlie", "preferences": [("David", 7)]},
            {"name": "David", "preferences": []},
        ]
        groups, group_scores, total_score = group_students(students, group_size=2)

        self.assertEqual(len(groups), 2)
        self.assertTrue(all(len(group) == 2 for group in groups))
        self.assertEqual(total_score, 17)  

    def test_all_students_in_groups(self):
        """
        Checks that all students are assigned to a unique group.
        Each group has a size between 1 and group_size.
        """
        students = [{"name": f"Student{i}", "preferences": []} for i in range(10)]
        group_size = 3
        groups, group_scores, total_score = group_students(students, group_size=group_size)

        all_assigned = sum(len(g) for g in groups)
        self.assertEqual(all_assigned, len(students))
        self.assertTrue(all(1 <= len(group) <= group_size for group in groups))


    def test_group_sizes_with_remainder(self):
        """
        Tests for correct group allocation when the number of students
        is not an exact multiple of the group size.
        """
        students = [{"name": f"Student{i}", "preferences": []} for i in range(7)]
        group_size = 3
        groups, group_scores, total_score = group_students(students, group_size=group_size)

        expected_group_counts = [3, 2, 2]  
        actual_group_counts = [len(g) for g in groups]

        self.assertEqual(sorted(expected_group_counts), sorted(actual_group_counts))

        
if __name__ == "__main__":
    unittest.main()