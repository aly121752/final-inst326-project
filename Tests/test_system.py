"""
System tests for the Student Gradebook System.

Tests complete end-to-end workflows.
Required: 3-5 system tests.
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Homework, Quiz, Project, Exam, Student, Teacher, Gradebook
from src.persistence import DataStore
from src.app import GradebookApp


class TestTeacherWorkflowEndToEnd(unittest.TestCase):
    """
    System Test 1: Complete teacher workflow.
    
    Tests: Login -> View dashboard -> Add grades -> Save -> Verify persistence
    """
    
    def setUp(self):
        """Create temp directory and app."""
        self.temp_dir = tempfile.mkdtemp()
        self.app = GradebookApp(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)
    
    def test_teacher_complete_workflow(self):
        """Test complete teacher workflow from login to grade management."""
        # Step 1: Login as teacher
        success, msg = self.app.login("t001", "teach123")
        self.assertTrue(success)
        self.assertTrue(self.app.is_teacher())
        
        # Step 2: View dashboard
        dashboard = self.app.display_teacher_dashboard()
        self.assertIn("TEACHER DASHBOARD", dashboard)
        self.assertIn("Dr. Amanda Johnson", dashboard)
        
        # Step 3: Add a grade
        success, msg = self.app.add_grade(
            student_id="s001",
            class_name="INST326",
            assignment_name="New Assignment",
            assignment_type="homework",
            points=95,
            max_points=100
        )
        self.assertTrue(success)
        
        # Step 4: Verify grade was added
        student = self.app.gradebook.get_student("s001")
        self.assertIn("New Assignment", student.grades["INST326"])
        
        # Step 5: Save data
        success, msg = self.app.save_data()
        self.assertTrue(success)
        
        # Step 6: Create new app and verify data persists
        new_app = GradebookApp(data_dir=self.temp_dir)
        student = new_app.gradebook.get_student("s001")
        self.assertIn("New Assignment", student.grades["INST326"])


class TestStudentWorkflowEndToEnd(unittest.TestCase):
    """
    System Test 2: Complete student workflow.
    
    Tests: Login -> View grades -> Verify calculations
    """
    
    def setUp(self):
        """Create app."""
        self.temp_dir = tempfile.mkdtemp()
        self.app = GradebookApp(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)
    
    def test_student_view_grades_workflow(self):
        """Test complete student workflow for viewing grades."""
        # Step 1: Login as student
        success, msg = self.app.login("s001", "student123")
        self.assertTrue(success)
        self.assertTrue(self.app.is_student())
        
        # Step 2: View dashboard
        dashboard = self.app.display_student_dashboard()
        self.assertIn("STUDENT DASHBOARD", dashboard)
        self.assertIn("John Kirk", dashboard)
        
        # Step 3: Verify grade data is displayed
        self.assertIn("INST326", dashboard)
        
        # Step 4: Verify student cannot add grades
        success, msg = self.app.add_grade("s001", "INST326", "Test", "homework", 100, 100)
        self.assertFalse(success)
        self.assertIn("Access denied", msg)
        
        # Step 5: Logout
        logout_msg = self.app.logout()
        self.assertIn("Goodbye", logout_msg)
        self.assertIsNone(self.app.get_current_user())


class TestCsvImportExportWorkflow(unittest.TestCase):
    """
    System Test 3: Complete CSV import/export workflow.
    
    Tests: Import CSV -> Verify data -> Export report -> Verify export
    """
    
    def setUp(self):
        """Create temp directory and test CSV."""
        self.temp_dir = tempfile.mkdtemp()
        self.app = GradebookApp(data_dir=self.temp_dir)
        
        # Create import CSV
        self.import_csv = Path(self.temp_dir) / "import_test.csv"
        with open(self.import_csv, 'w') as f:
            f.write("student_id,student_name,class_name,assignment_name,assignment_type,points,max_points,week\n")
            f.write("s100,Test Student,INST326,Import HW,homework,88,100,5\n")
            f.write("s100,Test Student,INST326,Import Quiz,quiz,9,10,6\n")
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)
    
    def test_csv_import_export_workflow(self):
        """Test complete CSV import/export cycle."""
        # Step 1: Login as teacher
        self.app.login("t001", "teach123")
        
        # Step 2: Import grades from CSV
        imported, msg = self.app.import_grades_csv(str(self.import_csv))
        self.assertEqual(imported, 2)
        
        # Step 3: Verify imported data exists
        student = self.app.gradebook.get_student("s100")
        self.assertIsNotNone(student)
        self.assertEqual(student.name, "Test Student")
        self.assertIn("Import HW", student.grades["INST326"])
        
        # Step 4: Export report
        success, msg = self.app.export_report("exported_report.json")
        self.assertTrue(success)
        
        # Step 5: Verify export file exists and contains data
        export_path = Path(self.temp_dir) / "exported_report.json"
        self.assertTrue(export_path.exists())
        
        import json
        with open(export_path) as f:
            report = json.load(f)
        
        # Find our imported student in report
        student_ids = [s["student_id"] for s in report["students"]]
        self.assertIn("s100", student_ids)


class TestDataPersistenceWorkflow(unittest.TestCase):
    """
    System Test 4: Data persistence across sessions.
    
    Tests: Create data -> Save -> Close -> Reopen -> Verify data intact
    """
    
    def setUp(self):
        """Create temp directory."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)
    
    def test_data_persists_across_sessions(self):
        """Test that data survives application restart."""
        # Session 1: Create and save data
        app1 = GradebookApp(data_dir=self.temp_dir)
        app1.login("t001", "teach123")
        
        # Add multiple grades
        app1.add_grade("s001", "INST326", "Session1 HW", "homework", 90, 100)
        app1.add_grade("s002", "INST326", "Session1 Quiz", "quiz", 8, 10)
        
        # Save and "close" (delete reference)
        success, _ = app1.save_data()
        self.assertTrue(success)
        del app1
        
        # Session 2: Reopen and verify
        app2 = GradebookApp(data_dir=self.temp_dir)
        
        # Verify s001's grade
        s1 = app2.gradebook.get_student("s001")
        self.assertIn("Session1 HW", s1.grades["INST326"])
        self.assertEqual(s1.grades["INST326"]["Session1 HW"].points, 90)
        
        # Verify s002's grade
        s2 = app2.gradebook.get_student("s002")
        self.assertIn("Session1 Quiz", s2.grades["INST326"])
        
        # Session 3: Add more data and save again
        app2.login("t001", "teach123")
        success, msg = app2.add_grade("s001", "INST326", "Session2 Exam", "exam", 85, 100)
        self.assertTrue(success, f"Failed to add grade: {msg}")
        success, msg = app2.save_data()
        self.assertTrue(success, f"Failed to save: {msg}")
        del app2
        
        # Session 4: Final verification
        app3 = GradebookApp(data_dir=self.temp_dir)
        s1_final = app3.gradebook.get_student("s001")
        
        # Should have both session 1 and session 2 grades
        self.assertIn("Session1 HW", s1_final.grades["INST326"])
        self.assertIn("Session2 Exam", s1_final.grades["INST326"])


class TestFullGradingCycleWorkflow(unittest.TestCase):
    """
    System Test 5: Complete grading cycle from assignment creation to reporting.
    
    Tests the complete workflow a teacher would use in practice.
    """
    
    def setUp(self):
        """Create temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.app = GradebookApp(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)
    
    def test_full_grading_cycle(self):
        """Test complete grading cycle: add grades -> calculate averages -> export."""
        # Login as teacher
        self.app.login("t001", "teach123")
        
        # Grade all students on same assignment
        students = ["s001", "s002", "s003"]
        scores = [90, 85, 95]
        
        for sid, score in zip(students, scores):
            success, _ = self.app.add_grade(
                sid, "INST326", "Final Exam", "exam", score, 100
            )
            self.assertTrue(success)
        
        # Calculate and verify class average
        class_avg = self.app.gradebook.get_class_average("INST326")
        self.assertIsNotNone(class_avg)
        
        # Individual student averages should be calculable
        for sid in students:
            student = self.app.gradebook.get_student(sid)
            avg = student.get_class_average("INST326")
            self.assertIsNotNone(avg)
        
        # Export to CSV
        success, _ = self.app.export_csv("final_grades.csv")
        self.assertTrue(success)
        
        # Verify CSV contains our data
        csv_path = Path(self.temp_dir) / "final_grades.csv"
        self.assertTrue(csv_path.exists())
        
        with open(csv_path) as f:
            content = f.read()
        
        # All students should be in export
        for sid in students:
            self.assertIn(sid, content)
        
        self.assertIn("Final Exam", content)


if __name__ == "__main__":
    unittest.main()

