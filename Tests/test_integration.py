"""
Integration tests for the Student Gradebook System.

Tests how different classes and components work together.
Required: 5-8 integration tests.
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    Homework, Quiz, Project, Exam,
    Student, Teacher, Gradebook
)
from src.filters import FilterManager, ScoreRangeFilter, AssignmentTypeFilter
from src.persistence import DataStore


class TestGradebookStudentIntegration(unittest.TestCase):
    """Test integration between Gradebook and Student classes."""
    
    def setUp(self):
        """Set up gradebook with students."""
        self.gradebook = Gradebook()
        self.student = Student("s001", "John Doe", "CS")
        self.student.enroll("INST326")
        self.gradebook.add_student(self.student)
    
    def test_gradebook_adds_grade_to_student(self):
        """Test that adding grade through gradebook updates student."""
        hw = Homework("Lab 1", 85, 100)
        self.gradebook.add_grade("s001", "INST326", hw)
        
        # Verify student's grades are updated
        student = self.gradebook.get_student("s001")
        self.assertIn("Lab 1", student.grades["INST326"])
        self.assertEqual(student.grades["INST326"]["Lab 1"].points, 85)
    
    def test_gradebook_calculates_class_average_from_students(self):
        """Test that gradebook correctly aggregates student grades."""
        # Add second student
        student2 = Student("s002", "Jane Doe", "CS")
        student2.enroll("INST326")
        self.gradebook.add_student(student2)
        
        # Add grades: s001 gets 80, s002 gets 100
        self.gradebook.add_grade("s001", "INST326", Homework("HW 1", 80, 100))
        self.gradebook.add_grade("s002", "INST326", Homework("HW 1", 100, 100))
        
        # Class average should be 90
        avg = self.gradebook.get_class_average("INST326")
        self.assertEqual(avg, 90.0)


class TestPolymorphicGrading(unittest.TestCase):
    """Test that different assignment types work polymorphically in gradebook."""
    
    def test_multiple_assignment_types_in_student(self):
        """Test student can hold different assignment types."""
        student = Student("s001", "John Doe")
        student.enroll("Math")
        
        # Add different types
        student.add_assignment("Math", Homework("HW 1", 80, 100))  # 80%
        student.add_assignment("Math", Quiz("Quiz 1", 8, 10))       # 96% (1.2x weight, capped)
        student.add_assignment("Math", Project("Proj 1", 90, 100)) # 81% (0.9x weight)
        student.add_assignment("Math", Exam("Exam 1", 85, 100))    # 85%
        
        # Verify all types are stored and calculate correctly
        grades = student.grades["Math"]
        self.assertEqual(len(grades), 4)
        
        # Verify polymorphism - each calculates its own way
        self.assertEqual(grades["HW 1"].calculate_percentage(), 80.0)
        self.assertAlmostEqual(grades["Quiz 1"].calculate_percentage(), 96.0, places=1)
        self.assertEqual(grades["Proj 1"].calculate_percentage(), 81.0)
        self.assertEqual(grades["Exam 1"].calculate_percentage(), 85.0)


class TestGradebookTeacherIntegration(unittest.TestCase):
    """Test integration between Gradebook and Teacher classes."""
    
    def test_teacher_course_matches_student_enrollment(self):
        """Test teacher's courses align with student enrollments."""
        gradebook = Gradebook()
        
        # Create teacher teaching INST326
        teacher = Teacher("t001", "Dr. Smith", "Info Science")
        teacher.add_course("INST326")
        gradebook.add_teacher(teacher)
        
        # Create students in that course
        s1 = Student("s001", "Alice")
        s1.enroll("INST326")
        s2 = Student("s002", "Bob")
        s2.enroll("INST326")
        gradebook.add_student(s1)
        gradebook.add_student(s2)
        
        # Verify roster matches
        roster = gradebook.get_class_roster("INST326")
        self.assertEqual(len(roster), 2)
        self.assertIn("INST326", teacher.courses_taught)


class TestFilterGradebookIntegration(unittest.TestCase):
    """Test integration between filters and gradebook data."""
    
    def test_filter_student_grades_by_score_range(self):
        """Test filtering a student's grades by score."""
        student = Student("s001", "John")
        student.enroll("Math")
        student.add_assignment("Math", Homework("HW 1", 70, 100))
        student.add_assignment("Math", Homework("HW 2", 95, 100))
        student.add_assignment("Math", Homework("HW 3", 85, 100))
        
        # Convert to filterable format
        grade_dicts = [
            {"name": student.name, "assignment_type": "homework", 
             "score": a.calculate_percentage(), "week": a.week}
            for a in student.grades["Math"].values()
        ]
        
        # Filter for high scores (80+)
        fm = FilterManager()
        fm.add_filter(ScoreRangeFilter(80, 100))
        result = fm.apply_all(grade_dicts)
        
        # HW2 (95) and HW3 (85) pass, HW1 (70) does not
        self.assertEqual(len(result), 2)


class TestDataStoreGradebookIntegration(unittest.TestCase):
    """Test integration between DataStore and Gradebook (persistence)."""
    
    def setUp(self):
        """Create temp directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.datastore = DataStore(self.temp_dir)
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_gradebook(self):
        """Test complete save/load cycle preserves data."""
        # Create gradebook with data
        gradebook = Gradebook()
        student = Student("s001", "John Doe", "CS")
        student.enroll("INST326")
        student.add_assignment("INST326", Homework("Lab 1", 90, 100))
        gradebook.add_student(student)
        
        teacher = Teacher("t001", "Dr. Smith", "Info Science")
        teacher.add_course("INST326")
        gradebook.add_teacher(teacher)
        
        # Save
        success, msg = self.datastore.save_gradebook(gradebook)
        self.assertTrue(success)
        
        # Load into new gradebook
        loaded, msg = self.datastore.load_gradebook()
        self.assertIsNotNone(loaded)
        
        # Verify data integrity
        self.assertIn("s001", loaded.students)
        self.assertEqual(loaded.students["s001"].name, "John Doe")
        self.assertIn("Lab 1", loaded.students["s001"].grades["INST326"])
        self.assertIn("t001", loaded.teachers)


class TestCsvImportGradebookIntegration(unittest.TestCase):
    """Test CSV import integration with gradebook."""
    
    def setUp(self):
        """Create temp directory and CSV file."""
        self.temp_dir = tempfile.mkdtemp()
        self.datastore = DataStore(self.temp_dir)
        self.gradebook = Gradebook()
        
        # Create test CSV
        self.csv_path = Path(self.temp_dir) / "test_grades.csv"
        with open(self.csv_path, 'w') as f:
            f.write("student_id,student_name,class_name,assignment_name,assignment_type,points,max_points,week\n")
            f.write("s001,John Doe,INST326,Lab 1,homework,90,100,1\n")
            f.write("s001,John Doe,INST326,Quiz 1,quiz,9,10,2\n")
            f.write("s002,Jane Doe,INST326,Lab 1,homework,85,100,1\n")
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_csv_import_creates_students_and_grades(self):
        """Test that CSV import creates students and grades correctly."""
        imported, msg = self.datastore.import_grades_from_csv(
            self.gradebook, str(self.csv_path)
        )
        
        self.assertEqual(imported, 3)
        self.assertIn("s001", self.gradebook.students)
        self.assertIn("s002", self.gradebook.students)
        
        # Verify grades
        s1 = self.gradebook.get_student("s001")
        self.assertIn("Lab 1", s1.grades["INST326"])
        self.assertIn("Quiz 1", s1.grades["INST326"])


class TestGradebookExportIntegration(unittest.TestCase):
    """Test gradebook export functionality."""
    
    def setUp(self):
        """Set up gradebook and temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.datastore = DataStore(self.temp_dir)
        
        # Create gradebook with data
        self.gradebook = Gradebook()
        student = Student("s001", "John Doe", "CS")
        student.enroll("INST326")
        student.add_assignment("INST326", Homework("Lab 1", 90, 100))
        self.gradebook.add_student(student)
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_export_report_creates_json(self):
        """Test that report export creates valid JSON file."""
        success, msg = self.datastore.export_grades_report(
            self.gradebook, "test_report.json"
        )
        
        self.assertTrue(success)
        
        # Verify file exists and is valid JSON
        report_path = Path(self.temp_dir) / "test_report.json"
        self.assertTrue(report_path.exists())
        
        import json
        with open(report_path) as f:
            data = json.load(f)
        
        self.assertIn("summary", data)
        self.assertIn("students", data)
        self.assertEqual(data["summary"]["total_students"], 1)


class TestMultipleStudentGradebookIntegration(unittest.TestCase):
    """Test gradebook operations with multiple students."""
    
    def test_class_roster_filtering(self):
        """Test getting class roster filters correctly."""
        gradebook = Gradebook()
        
        # Students in different classes
        s1 = Student("s001", "Alice")
        s1.enroll("INST326")
        s1.enroll("CMSC131")
        
        s2 = Student("s002", "Bob")
        s2.enroll("INST326")
        
        s3 = Student("s003", "Charlie")
        s3.enroll("CMSC131")
        
        gradebook.add_student(s1)
        gradebook.add_student(s2)
        gradebook.add_student(s3)
        
        # Check rosters
        inst326_roster = gradebook.get_class_roster("INST326")
        cmsc131_roster = gradebook.get_class_roster("CMSC131")
        
        self.assertEqual(len(inst326_roster), 2)  # Alice and Bob
        self.assertEqual(len(cmsc131_roster), 2)  # Alice and Charlie
        
        # Verify specific students
        inst326_names = [s.name for s in inst326_roster]
        self.assertIn("Alice", inst326_names)
        self.assertIn("Bob", inst326_names)
        self.assertNotIn("Charlie", inst326_names)


if __name__ == "__main__":
    unittest.main()

