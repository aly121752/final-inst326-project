"""
Main application for the Student Gradebook System.

Provides a command-line interface for:
- User authentication (students and teachers)
- Viewing grades and dashboards
- Managing grades (teachers only)
- Data import/export
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
from .models import Gradebook, Student, Teacher, Homework, Quiz, Project, Exam
from .persistence import DataStore


class GradebookApp:
    """
    Main application class that handles user interaction.
    """
    
    def __init__(self, data_dir: str = "data"):
        self._datastore = DataStore(data_dir)
        self._gradebook: Optional[Gradebook] = None
        self._current_user: Optional[Dict] = None
        self._users: Dict[str, Dict] = {}
        
        # Initialize demo user credentials (always available)
        self._init_demo_users()
        
        # Try to load existing data
        self._load_or_create_gradebook()
    
    def _init_demo_users(self):
        """Initialize demo user credentials."""
        # Teacher accounts
        self._users["t001"] = {
            "password": "teach123", "role": "teacher",
            "name": "Dr. Amanda Johnson", "id": "t001"
        }
        self._users["t002"] = {
            "password": "teach123", "role": "teacher",
            "name": "Prof. Brian Smith", "id": "t002"
        }
        # Student accounts
        for sid, name in [("s001", "John Kirk"), ("s002", "Sarah Williams"), ("s003", "Maria Rodriguez")]:
            self._users[sid] = {
                "password": "student123", "role": "student",
                "name": name, "id": sid
            }
    
    def _load_or_create_gradebook(self):
        """Load existing gradebook or create a new one with sample data."""
        gradebook, message = self._datastore.load_gradebook()
        
        if gradebook:
            self._gradebook = gradebook
            print(f"Loaded existing data: {message}")
        else:
            self._gradebook = Gradebook()
            self._create_sample_data()
            print("Created new gradebook with sample data")
    
    def _create_sample_data(self):
        """Create sample students, teachers, and grades for demonstration."""
        # Create teachers
        teachers = [
            Teacher("t001", "Dr. Amanda Johnson", "Information Science"),
            Teacher("t002", "Prof. Brian Smith", "Computer Science"),
        ]
        for teacher in teachers:
            teacher.add_course("INST326")
            self._gradebook.add_teacher(teacher)
        
        # Create students
        students_data = [
            ("s001", "John Kirk", "Information Science", ["INST326", "ENGL101"]),
            ("s002", "Sarah Williams", "Computer Science", ["INST326", "CMSC131"]),
            ("s003", "Maria Rodriguez", "Business", ["INST326", "BMGT110"]),
        ]
        
        for sid, name, major, classes in students_data:
            student = Student(sid, name, major)
            for cls in classes:
                student.enroll(cls)
            self._gradebook.add_student(student)
        
        # Add some sample grades
        sample_grades = [
            ("s001", "INST326", Homework("Lab 1", 18, 20, 1)),
            ("s001", "INST326", Quiz("Quiz 1", 9, 10, 2)),
            ("s001", "INST326", Exam("Midterm", 85, 100, 8)),
            ("s002", "INST326", Homework("Lab 1", 20, 20, 1)),
            ("s002", "INST326", Quiz("Quiz 1", 8, 10, 2)),
            ("s002", "INST326", Project("Project 1", 92, 100, 5)),
            ("s003", "INST326", Homework("Lab 1", 17, 20, 1)),
            ("s003", "INST326", Quiz("Quiz 1", 7, 10, 2)),
        ]
        
        for sid, class_name, assignment in sample_grades:
            student = self._gradebook.get_student(sid)
            student.add_assignment(class_name, assignment)
    
    def login(self, user_id: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate a user.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if user_id not in self._users:
            return False, "Invalid user ID or password"
        
        user = self._users[user_id]
        if user["password"] != password:
            return False, "Invalid user ID or password"
        
        self._current_user = user
        return True, f"Welcome, {user['name']}!"
    
    def logout(self) -> str:
        """Log out the current user."""
        if self._current_user:
            name = self._current_user["name"]
            self._current_user = None
            return f"Goodbye, {name}!"
        return "No user logged in"
    
    def get_current_user(self) -> Optional[Dict]:
        """Get the currently logged in user."""
        return self._current_user
    
    def is_teacher(self) -> bool:
        """Check if current user is a teacher."""
        return self._current_user and self._current_user.get("role") == "teacher"
    
    def is_student(self) -> bool:
        """Check if current user is a student."""
        return self._current_user and self._current_user.get("role") == "student"
    
    def display_student_dashboard(self) -> str:
        """Display dashboard for a student."""
        if not self._current_user or self._current_user["role"] != "student":
            return "Access denied: Student login required"
        
        student = self._gradebook.get_student(self._current_user["id"])
        if not student:
            return "Student not found"
        
        lines = [
            f"\n{'='*50}",
            f"STUDENT DASHBOARD - {student.name}",
            f"{'='*50}",
            f"Major: {student.major}",
            f"Overall Average: {student.get_overall_average() or 'N/A'}%",
            ""
        ]
        
        for class_name in student.classes:
            avg = student.get_class_average(class_name)
            lines.append(f"\n{class_name} (Average: {avg or 'N/A'}%)")
            lines.append("-" * 30)
            
            assignments = student.grades.get(class_name, {})
            if assignments:
                for assign in assignments.values():
                    pct = assign.calculate_percentage()
                    lines.append(f"  {assign.name}: {assign.points}/{assign.max_points} ({pct:.1f}%)")
            else:
                lines.append("  No grades yet")
        
        return "\n".join(lines)
    
    def display_teacher_dashboard(self) -> str:
        """Display dashboard for a teacher."""
        if not self._current_user or self._current_user["role"] != "teacher":
            return "Access denied: Teacher login required"
        
        teacher = self._gradebook.get_teacher(self._current_user["id"])
        if not teacher:
            return "Teacher not found"
        
        lines = [
            f"\n{'='*50}",
            f"TEACHER DASHBOARD - {teacher.name}",
            f"{'='*50}",
            f"Department: {teacher.department}",
            ""
        ]
        
        for course_code in teacher.courses_taught:
            class_avg = self._gradebook.get_class_average(course_code)
            roster = self._gradebook.get_class_roster(course_code)
            
            lines.append(f"\n{course_code} (Class Average: {class_avg or 'N/A'}%)")
            lines.append("-" * 40)
            lines.append(f"Enrolled Students: {len(roster)}")
            
            for student in roster:
                avg = student.get_class_average(course_code)
                lines.append(f"  - {student.name}: {avg or 'N/A'}%")
        
        return "\n".join(lines)
    
    def add_grade(self, student_id: str, class_name: str, 
                  assignment_name: str, assignment_type: str,
                  points: float, max_points: float, week: int = 1) -> Tuple[bool, str]:
        """Add a grade (teacher only)."""
        if not self.is_teacher():
            return False, "Access denied: Teacher login required"
        
        assignment_classes = {
            'homework': Homework,
            'quiz': Quiz,
            'project': Project,
            'exam': Exam
        }
        
        AssignmentClass = assignment_classes.get(assignment_type.lower(), Homework)
        
        try:
            assignment = AssignmentClass(assignment_name, points, max_points, week)
            self._gradebook.add_grade(student_id, class_name, assignment)
            return True, f"Grade added for {student_id} in {class_name}"
        except (KeyError, ValueError) as e:
            return False, str(e)
    
    def save_data(self) -> Tuple[bool, str]:
        """Save the current gradebook state."""
        return self._datastore.save_gradebook(self._gradebook)
    
    def import_grades_csv(self, filepath: str) -> Tuple[int, str]:
        """Import grades from CSV."""
        return self._datastore.import_grades_from_csv(self._gradebook, filepath)
    
    def export_report(self, filename: str = "grades_report.json") -> Tuple[bool, str]:
        """Export grades report."""
        return self._datastore.export_grades_report(self._gradebook, filename)
    
    def export_csv(self, filename: str = "grades_export.csv") -> Tuple[bool, str]:
        """Export grades to CSV."""
        return self._datastore.export_grades_to_csv(self._gradebook, filename)
    
    @property
    def gradebook(self) -> Gradebook:
        """Access the underlying gradebook."""
        return self._gradebook


def main():
    """Main entry point for the application."""
    app = GradebookApp()
    
    print("\n" + "="*50)
    print("STUDENT GRADEBOOK SYSTEM")
    print("="*50)
    print("\nSample Users:")
    print("  Students: s001, s002, s003 (password: student123)")
    print("  Teachers: t001, t002 (password: teach123)")
    
    while True:
        print("\n" + "-"*30)
        if app.get_current_user():
            user = app.get_current_user()
            print(f"Logged in as: {user['name']} ({user['role']})")
            print("\nOptions:")
            print("  1. View Dashboard")
            print("  2. Save Data")
            print("  3. Export Report")
            print("  4. Logout")
            if app.is_teacher():
                print("  5. Add Grade")
        else:
            print("Options:")
            print("  1. Login")
            print("  2. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if not app.get_current_user():
            if choice == "1":
                user_id = input("User ID: ").strip()
                password = input("Password: ").strip()
                success, msg = app.login(user_id, password)
                print(msg)
            elif choice == "2":
                print("Goodbye!")
                break
        else:
            if choice == "1":
                if app.is_student():
                    print(app.display_student_dashboard())
                else:
                    print(app.display_teacher_dashboard())
            elif choice == "2":
                success, msg = app.save_data()
                print(msg)
            elif choice == "3":
                success, msg = app.export_report()
                print(msg)
            elif choice == "4":
                print(app.logout())
            elif choice == "5" and app.is_teacher():
                student_id = input("Student ID: ").strip()
                class_name = input("Class: ").strip()
                assign_name = input("Assignment name: ").strip()
                assign_type = input("Type (homework/quiz/project/exam): ").strip()
                points = float(input("Points earned: ").strip())
                max_points = float(input("Max points: ").strip())
                success, msg = app.add_grade(student_id, class_name, assign_name, 
                                            assign_type, points, max_points)
                print(msg)


if __name__ == "__main__":
    main()

