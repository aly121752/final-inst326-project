"""
Unit tests for the Student Gradebook System.

Tests individual classes and methods in isolation.
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    AbstractAssignment, Homework, Quiz, Project, Exam,
    Student, Teacher, Gradebook
)
from src.filters import (
    AssignmentTypeFilter, LateSubmissionFilter, ScoreRangeFilter,
    StudentNameFilter, WeekFilter, FilterManager,
    filter_by_assignment_type, filter_by_score_range
)


class TestAbstractAssignment(unittest.TestCase):
    """Test that AbstractAssignment cannot be instantiated."""
    
    def test_cannot_instantiate_abstract_assignment(self):
        """Abstract class should raise TypeError on instantiation."""
        with self.assertRaises(TypeError):
            AbstractAssignment("Test", 10, 10)


class TestHomework(unittest.TestCase):
    """Tests for Homework assignment type."""
    
    def test_create_homework(self):
        """Test creating a homework assignment."""
        hw = Homework("Lab 1", 85, 100)
        self.assertEqual(hw.name, "Lab 1")
        self.assertEqual(hw.points, 85)
        self.assertEqual(hw.max_points, 100)
    
    def test_calculate_percentage(self):
        """Test homework percentage calculation (standard)."""
        hw = Homework("Lab 1", 80, 100)
        self.assertEqual(hw.calculate_percentage(), 80.0)
    
    def test_update_score(self):
        """Test updating homework scores."""
        hw = Homework("Lab 1", 50, 100)
        hw.update(90, 100)
        self.assertEqual(hw.calculate_percentage(), 90.0)
    
    def test_invalid_name_raises_error(self):
        """Empty name should raise ValueError."""
        with self.assertRaises(ValueError):
            Homework("", 85, 100)
    
    def test_invalid_max_points_raises_error(self):
        """Zero or negative max_points should raise ValueError."""
        with self.assertRaises(ValueError):
            Homework("Lab 1", 85, 0)


class TestQuiz(unittest.TestCase):
    """Tests for Quiz assignment type with 1.2x weight."""
    
    def test_quiz_weighted_percentage(self):
        """Quiz should apply 1.2x weight."""
        quiz = Quiz("Quiz 1", 8, 10)
        # 8/10 * 1.2 = 0.96 -> 96%
        self.assertAlmostEqual(quiz.calculate_percentage(), 96.0, places=1)
    
    def test_quiz_capped_at_100(self):
        """Quiz score should cap at 100%."""
        quiz = Quiz("Quiz 1", 10, 10)
        # 10/10 * 1.2 = 1.2 -> capped at 100%
        self.assertEqual(quiz.calculate_percentage(), 100.0)


class TestProject(unittest.TestCase):
    """Tests for Project assignment type with 0.9x weight."""
    
    def test_project_weighted_percentage(self):
        """Project should apply 0.9x weight."""
        proj = Project("Project 1", 90, 100)
        # 90/100 * 0.9 = 0.81 -> 81%
        self.assertEqual(proj.calculate_percentage(), 81.0)


class TestExam(unittest.TestCase):
    """Tests for Exam assignment type."""
    
    def test_exam_standard_percentage(self):
        """Exam should use standard percentage."""
        exam = Exam("Midterm", 85, 100)
        self.assertEqual(exam.calculate_percentage(), 85.0)


class TestStudent(unittest.TestCase):
    """Tests for Student class."""
    
    def test_create_student(self):
        """Test creating a student."""
        student = Student("s001", "John Doe", "Computer Science")
        self.assertEqual(student.student_id, "s001")
        self.assertEqual(student.name, "John Doe")
        self.assertEqual(student.major, "Computer Science")
    
    def test_enroll_in_class(self):
        """Test enrolling in a class."""
        student = Student("s001", "John Doe")
        student.enroll("INST326")
        self.assertIn("INST326", student.classes)
    
    def test_add_assignment(self):
        """Test adding an assignment after enrollment."""
        student = Student("s001", "John Doe")
        student.enroll("Math")
        hw = Homework("HW 1", 100, 100)
        student.add_assignment("Math", hw)
        self.assertIn("HW 1", student.grades["Math"])
    
    def test_add_assignment_without_enrollment_raises(self):
        """Adding assignment to unenrolled class should raise KeyError."""
        student = Student("s001", "John Doe")
        hw = Homework("HW 1", 100, 100)
        with self.assertRaises(KeyError):
            student.add_assignment("Math", hw)
    
    def test_get_class_average(self):
        """Test calculating class average."""
        student = Student("s001", "John Doe")
        student.enroll("Math")
        student.add_assignment("Math", Homework("HW 1", 80, 100))
        student.add_assignment("Math", Homework("HW 2", 90, 100))
        # (80 + 90) / 2 = 85
        self.assertEqual(student.get_class_average("Math"), 85.0)
    
    def test_empty_student_id_raises_error(self):
        """Empty student_id should raise ValueError."""
        with self.assertRaises(ValueError):
            Student("", "John Doe")


class TestTeacher(unittest.TestCase):
    """Tests for Teacher class."""
    
    def test_create_teacher(self):
        """Test creating a teacher."""
        teacher = Teacher("t001", "Dr. Smith", "Computer Science")
        self.assertEqual(teacher.teacher_id, "t001")
        self.assertEqual(teacher.name, "Dr. Smith")
        self.assertEqual(teacher.department, "Computer Science")
    
    def test_add_course(self):
        """Test adding a course to teaching load."""
        teacher = Teacher("t001", "Dr. Smith", "CS")
        teacher.add_course("INST326")
        self.assertIn("INST326", teacher.courses_taught)
    
    def test_empty_name_raises_error(self):
        """Empty name should raise ValueError."""
        with self.assertRaises(ValueError):
            Teacher("t001", "", "CS")


class TestGradebook(unittest.TestCase):
    """Tests for Gradebook class."""
    
    def test_add_student(self):
        """Test adding a student to gradebook."""
        gb = Gradebook()
        student = Student("s001", "John Doe")
        gb.add_student(student)
        self.assertIn("s001", gb.students)
    
    def test_get_student(self):
        """Test retrieving a student."""
        gb = Gradebook()
        student = Student("s001", "John Doe")
        gb.add_student(student)
        retrieved = gb.get_student("s001")
        self.assertEqual(retrieved.name, "John Doe")
    
    def test_add_grade_through_gradebook(self):
        """Test adding grade through gradebook."""
        gb = Gradebook()
        student = Student("s001", "John Doe")
        student.enroll("Math")
        gb.add_student(student)
        
        hw = Homework("HW 1", 90, 100)
        gb.add_grade("s001", "Math", hw)
        
        self.assertIn("HW 1", gb.students["s001"].grades["Math"])
    
    def test_add_grade_missing_student_raises(self):
        """Adding grade for non-existent student should raise."""
        gb = Gradebook()
        hw = Homework("HW 1", 90, 100)
        with self.assertRaises(KeyError):
            gb.add_grade("s999", "Math", hw)


class TestFilters(unittest.TestCase):
    """Tests for grade filtering functionality."""
    
    def setUp(self):
        """Set up sample grade data."""
        self.sample_grades = [
            {"name": "Alex", "assignment_type": "quiz", "score": 85, "is_late": False, "week": 1},
            {"name": "Alex", "assignment_type": "exam", "score": 92, "is_late": True, "week": 2},
            {"name": "Maria", "assignment_type": "quiz", "score": 60, "is_late": True, "week": 1},
            {"name": "Jin", "assignment_type": "homework", "score": 77, "is_late": False, "week": 3},
        ]
    
    def test_filter_by_assignment_type(self):
        """Test filtering by assignment type."""
        result = filter_by_assignment_type(self.sample_grades, "quiz")
        self.assertEqual(len(result), 2)
        for r in result:
            self.assertEqual(r["assignment_type"], "quiz")
    
    def test_filter_by_score_range(self):
        """Test filtering by score range."""
        result = filter_by_score_range(self.sample_grades, 80, 100)
        self.assertEqual(len(result), 2)
        for r in result:
            self.assertGreaterEqual(r["score"], 80)
    
    def test_late_submission_filter(self):
        """Test filtering late submissions."""
        f = LateSubmissionFilter()
        result = f.apply(self.sample_grades)
        self.assertEqual(len(result), 2)
        for r in result:
            self.assertTrue(r["is_late"])
    
    def test_filter_manager_stacking(self):
        """Test applying multiple filters."""
        fm = FilterManager()
        fm.add_filter(AssignmentTypeFilter("quiz"))
        fm.add_filter(ScoreRangeFilter(70, 100))
        
        result = fm.apply_all(self.sample_grades)
        # Only Alex's quiz (85) passes both filters
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alex")


class TestAssignmentSerialization(unittest.TestCase):
    """Test assignment to_dict and from_dict."""
    
    def test_homework_to_dict(self):
        """Test converting homework to dictionary."""
        hw = Homework("Lab 1", 85, 100, week=3)
        d = hw.to_dict()
        self.assertEqual(d["type"], "Homework")
        self.assertEqual(d["name"], "Lab 1")
        self.assertEqual(d["points"], 85)
    
    def test_from_dict_creates_correct_type(self):
        """Test factory method creates correct assignment type."""
        data = {"type": "Quiz", "name": "Quiz 1", "points": 8, "max_points": 10, "week": 2}
        assignment = AbstractAssignment.from_dict(data)
        self.assertIsInstance(assignment, Quiz)


class TestStudentSerialization(unittest.TestCase):
    """Test student to_dict and from_dict."""
    
    def test_student_round_trip(self):
        """Test converting student to dict and back."""
        student = Student("s001", "John Doe", "CS")
        student.enroll("Math")
        student.add_assignment("Math", Homework("HW 1", 90, 100))
        
        d = student.to_dict()
        restored = Student.from_dict(d)
        
        self.assertEqual(restored.student_id, "s001")
        self.assertEqual(restored.name, "John Doe")
        self.assertIn("Math", restored.classes)
        self.assertIn("HW 1", restored.grades["Math"])


if __name__ == "__main__":
    unittest.main()

