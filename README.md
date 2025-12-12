# Student Gradebook System

**Course:** INST326 - Object-Oriented Programming for Information Science

## Project Overview

A complete gradebook management system for educational environments that allows teachers to manage student grades and students to view their academic performance. The system features data persistence, CSV import/export capabilities, and comprehensive grade filtering.

### Key Features

- **User Authentication**: Role-based access for students and teachers
- **Grade Management**: Add, update, and delete grades with multiple assignment types
- **Data Persistence**: Save/load system state to JSON files
- **CSV Import/Export**: Import grades from CSV, export reports
- **Grade Filtering**: Filter by assignment type, score range, week, and more
- **Polymorphic Assignment Types**: Homework, Quiz, Project, Exam with different scoring

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/The-Variables-.git
   cd The-Variables-
   ```

2. **No external dependencies required** - uses Python standard library only (Python 3.7+)

3. **Run the application:**
   ```bash
   python -m src.app
   ```

## Quick Usage

### Running the Application

```bash
python -m src.app
```

### Sample Login Credentials

| Role    | User ID | Password    |
|---------|---------|-------------|
| Teacher | t001    | teach123    |
| Teacher | t002    | teach123    |
| Student | s001    | student123  |
| Student | s002    | student123  |
| Student | s003    | student123  |

### Using as a Library

```python
from src.models import Student, Gradebook, Homework, Quiz
from src.persistence import DataStore

# Create gradebook and add students
gradebook = Gradebook()
student = Student("s001", "John Doe", "Computer Science")
student.enroll("INST326")
gradebook.add_student(student)

# Add grades (polymorphic - any assignment type works)
student.add_assignment("INST326", Homework("Lab 1", 90, 100))
student.add_assignment("INST326", Quiz("Quiz 1", 9, 10))

# Calculate averages
print(f"Class Average: {student.get_class_average('INST326')}%")

# Save to file
datastore = DataStore("data")
datastore.save_gradebook(gradebook)
```

### Filtering Grades

```python
from src.filters import filter_by_assignment_type, FilterManager, ScoreRangeFilter

grades = [
    {"name": "Alex", "assignment_type": "quiz", "score": 85},
    {"name": "Maria", "assignment_type": "exam", "score": 92},
]

# Simple filtering
quizzes = filter_by_assignment_type(grades, "quiz")

# Composable filters
fm = FilterManager()
fm.add_filter(ScoreRangeFilter(80, 100))
high_scores = fm.apply_all(grades)
```

## Project Structure

```
The-Variables-/
├── src/
│   ├── __init__.py      # Package exports
│   ├── models.py        # Core classes (Student, Teacher, Gradebook, Assignments)
│   ├── filters.py       # Grade filtering system
│   ├── persistence.py   # JSON/CSV save/load/import/export
│   └── app.py           # Main application with CLI
├── tests/
│   ├── __init__.py
│   ├── test_unit.py         # Unit tests
│   ├── test_integration.py  # Integration tests (8 tests)
│   └── test_system.py       # System tests (5 tests)
├── data/
│   ├── sample_grades.csv    # Sample grade data for import
│   └── sample_students.csv  # Sample student data
├── docs/                    # Documentation files
└── README.md
```

## Architecture

### Class Hierarchy

```
AbstractAssignment (ABC)
├── Homework      (standard percentage)
├── Quiz          (1.2x weight, capped at 100%)
├── Project       (0.9x weight)
└── Exam          (standard percentage)

Student           (has classes and grades - composition)
Teacher           (has courses taught)
Gradebook         (has students and teachers - composition)

GradeFilter (ABC)
├── AssignmentTypeFilter
├── ScoreRangeFilter
├── LateSubmissionFilter
├── StudentNameFilter
├── WeekFilter
└── PassingScoreFilter

FilterManager     (has filters - composition)
DataStore         (handles persistence)
GradebookApp      (main application)
```

### OOP Concepts Demonstrated

| Concept | Implementation |
|---------|----------------|
| **Inheritance** | Assignment types inherit from AbstractAssignment |
| **Polymorphism** | Different calculate_percentage() per assignment type |
| **Abstraction** | ABC for AbstractAssignment and GradeFilter |
| **Composition** | Student has grades, Gradebook has students |
| **Encapsulation** | Private attributes with property access |

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Or using unittest
python -m unittest discover tests/

# Run specific test files
python -m unittest tests.test_unit
python -m unittest tests.test_integration
python -m unittest tests.test_system
```

### Test Coverage

- **Unit Tests**: 25+ tests covering individual classes and methods
- **Integration Tests**: 8 tests verifying component interactions
- **System Tests**: 5 end-to-end workflow tests

## Data Persistence

### Save/Load System State

```python
from src.persistence import DataStore
from src.models import Gradebook

datastore = DataStore("data")

# Save
datastore.save_gradebook(gradebook, "my_gradebook.json")

# Load
gradebook, message = datastore.load_gradebook("my_gradebook.json")
```

### Import from CSV

```python
# CSV format: student_id,student_name,class_name,assignment_name,assignment_type,points,max_points,week
imported, msg = datastore.import_grades_from_csv(gradebook, "data/sample_grades.csv")
```

### Export Reports

```python
# Export to JSON report
datastore.export_grades_report(gradebook, "report.json")

# Export to CSV
datastore.export_grades_to_csv(gradebook, "grades.csv")
```

## Video Presentation

[Link to presentation video - TBD]

## License

This project was created for INST326 at the University of Maryland.
