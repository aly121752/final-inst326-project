"""
Demo script showing the Student Gradebook System functionality.

Run from project root:
    python examples/demo.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Student, Teacher, Gradebook, Homework, Quiz, Project, Exam
from src.filters import filter_by_assignment_type, filter_by_score_range, FilterManager, ScoreRangeFilter
from src.persistence import DataStore


def demo_basic_usage():
    """Demonstrate basic gradebook usage."""
    print("=" * 50)
    print("DEMO: Basic Gradebook Usage")
    print("=" * 50)
    
    # Create a gradebook
    gradebook = Gradebook()
    
    # Create and add a student
    student = Student("s001", "Alice Johnson", "Computer Science")
    student.enroll("INST326")
    student.enroll("CMSC131")
    gradebook.add_student(student)
    
    # Create and add a teacher
    teacher = Teacher("t001", "Dr. Smith", "Information Science")
    teacher.add_course("INST326")
    gradebook.add_teacher(teacher)
    
    print(f"\nCreated: {student}")
    print(f"Created: {teacher}")
    print(f"Gradebook: {gradebook}")


def demo_polymorphic_assignments():
    """Demonstrate polymorphic assignment types."""
    print("\n" + "=" * 50)
    print("DEMO: Polymorphic Assignment Types")
    print("=" * 50)
    
    student = Student("s001", "Bob Williams")
    student.enroll("Math")
    
    # Add different assignment types - each calculates percentage differently
    assignments = [
        Homework("HW 1", 80, 100),      # Standard: 80%
        Quiz("Quiz 1", 8, 10),           # 1.2x weight: 96%
        Project("Project 1", 90, 100),   # 0.9x weight: 81%
        Exam("Midterm", 85, 100),        # Standard: 85%
    ]
    
    for assign in assignments:
        student.add_assignment("Math", assign)
        print(f"{assign.__class__.__name__}: {assign.points}/{assign.max_points} = {assign.calculate_percentage():.1f}%")
    
    print(f"\nClass Average: {student.get_class_average('Math'):.1f}%")


def demo_filtering():
    """Demonstrate grade filtering."""
    print("\n" + "=" * 50)
    print("DEMO: Grade Filtering")
    print("=" * 50)
    
    # Sample grade data (dict format for filtering)
    grades = [
        {"name": "Alice", "assignment_type": "quiz", "score": 85, "week": 1},
        {"name": "Alice", "assignment_type": "exam", "score": 92, "week": 2},
        {"name": "Bob", "assignment_type": "quiz", "score": 78, "week": 1},
        {"name": "Bob", "assignment_type": "homework", "score": 95, "week": 1},
        {"name": "Charlie", "assignment_type": "quiz", "score": 60, "week": 1},
    ]
    
    print(f"\nOriginal grades: {len(grades)} records")
    
    # Filter by assignment type
    quizzes = filter_by_assignment_type(grades, "quiz")
    print(f"Quizzes only: {len(quizzes)} records")
    
    # Filter by score range
    high_scores = filter_by_score_range(grades, 80, 100)
    print(f"High scores (80-100): {len(high_scores)} records")
    
    # Compose multiple filters
    fm = FilterManager()
    fm.add_filter(ScoreRangeFilter(70, 100))
    combined = fm.apply_all(grades)
    print(f"Score 70+: {len(combined)} records")


def demo_persistence():
    """Demonstrate save/load functionality."""
    print("\n" + "=" * 50)
    print("DEMO: Data Persistence")
    print("=" * 50)
    
    import tempfile
    import shutil
    
    # Use temp directory
    temp_dir = tempfile.mkdtemp()
    datastore = DataStore(temp_dir)
    
    try:
        # Create and populate gradebook
        gradebook = Gradebook()
        student = Student("s001", "Test Student", "CS")
        student.enroll("INST326")
        student.add_assignment("INST326", Homework("Lab 1", 95, 100))
        gradebook.add_student(student)
        
        # Save
        success, msg = datastore.save_gradebook(gradebook)
        print(f"\nSave: {msg}")
        
        # Load into new gradebook
        loaded, msg = datastore.load_gradebook()
        print(f"Load: {msg}")
        
        if loaded:
            print(f"Loaded student: {loaded.get_student('s001')}")
        
        # Export CSV
        success, msg = datastore.export_grades_to_csv(gradebook, "demo_export.csv")
        print(f"Export: {msg}")
        
    finally:
        shutil.rmtree(temp_dir)


def demo_csv_import():
    """Demonstrate CSV import."""
    print("\n" + "=" * 50)
    print("DEMO: CSV Import")
    print("=" * 50)
    
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    datastore = DataStore(temp_dir)
    
    try:
        # Create test CSV
        csv_path = Path(temp_dir) / "test_grades.csv"
        with open(csv_path, 'w') as f:
            f.write("student_id,student_name,class_name,assignment_name,assignment_type,points,max_points,week\n")
            f.write("s100,New Student,INST326,Imported HW,homework,88,100,1\n")
            f.write("s100,New Student,INST326,Imported Quiz,quiz,9,10,2\n")
        
        gradebook = Gradebook()
        imported, msg = datastore.import_grades_from_csv(gradebook, str(csv_path))
        print(f"\n{msg}")
        
        student = gradebook.get_student("s100")
        if student:
            print(f"Imported student: {student}")
            print(f"Class average: {student.get_class_average('INST326'):.1f}%")
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    demo_basic_usage()
    demo_polymorphic_assignments()
    demo_filtering()
    demo_persistence()
    demo_csv_import()
    
    print("\n" + "=" * 50)
    print("Demo complete!")
    print("=" * 50)

