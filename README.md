# Student Gradebook System

**Course:** INST326 - Object-Oriented Programming for Information Science

Student Gradebook System
Team: Matti Wakiwaya, Nailah Abdulbarr, Tidjani Sidi Ahmed, Andrew Ly (The-Variables) Domain: Student Gradebook Course: INST326 - Object-Oriented Programming for Information Science

Project Overview
The domain of this project lies within the field of educational technology, focusing specifically on digital grade management systems. In modern educational environments, teachers and students rely heavily on accurate and accessible tools to track academic performance. However, many existing systems are outdated, difficult to navigate, or lack key features that promote transparency and engagement. Our project seeks to bridge this gap by developing a platform that integrates intuitive design, secure access, and analytical tools, empowering both educators and learners to better understand and manage academic progress.

Problem Statement
Academic environments often lack simple tools that allow teachers to:

Add and manage student grades
Import grade data from CSV files
Export summary reports
View class averages
Preserve data between sessions Students need a quick way to view their grades without modifying system data.Many schools lack an efficient, secure, and user-friendly system for managing and communicating student grades, resulting in disorganization, limited accessibility, and reduced academic transparency.
#Overall Goal:

To streamline academic performance tracking while ensuring ease of use, data security, and effective communication between students and teachers
Installation and Setup
Clone this repository: git clone https://github.com/your-username/gradebook-information-system.git cd gradebook-information-system

No external dependencies required - uses Python standard library only

Run the application python app.py mac: python3 app.py

Installation Set-Up To set up and run the Student Gradebook project locally:

-Clone the repository from GitHub. -Navigate to the main project directory. -(Optional) Create and activate a virtual environment to manage dependencies. -Install all required dependencies listed in the requirements file. -Open the examples folder to view and run the demo script -Explore the source code inside the src folder to understand the project’s structure and functionality. -Refer to the docs directory for detailed documentation and function usage instructions.

Quick Usage Examples
Login (Default teacher account): Username: admin Password: pass

Add a Grade:

Add grade Student username: bob Assignment: Lab1 Score: 95
##System Overview

The system contains three major components:

#User Management:

User (base class)
Student
Teacher
Password validation
Role-based access (student vs teacher menu) #Gradebook:
Stores all grade data
Computes class average
Assignment-level retrieval
Handles updates from CSV import #Datastore (Persistence Layer):
Saves full system state to JSON
Loads data from previous sessions
Imports grades from CSV
Exports reports to JSON
Graceful error handling for missing/corrupt files
#Testing Overview: Unit Tests:

User creation + authentication
Gradebook grade storage and class averages
Datastore save/load functions Integration Tests:
Gradebook ↔ Datastore interaction
CSV import flow
User + gradebook combined operations System Tests:
End-to-end teacher workflow
Student grade retrieval after reload
CSV → JSON report end-to-end
Function List The project’s main functions are organized within the src/ directory to ensure modularity and clarity. Each team member contributed specific functional components:

Nailah – Grade Management Functions

addGrade(student, grade) – Adds a new grade entry for a student. updateGrade(student, index, new_grade) – Updates an existing grade. deleteGrade(gradeId) – Removes a grade from the record. view_grades() – Displays all recorded grades for review.

Andrew – Filtering Functions

filter_by_assignment_type(grades_list, assignment_type) – Filters grades by assignment type (e.g., quiz, exam, homework). filter_late_submissions(grades_list) – Filters out all assignments that were submitted late. filter_by_score_range(grades_list, min_score, max_score) – Filters students based on a score range. filter_by_student_name(grades_list, student_name) – Retrieves all grade entries for a specific student (case-insensitive). filter_by_week(grades_list, week_number) – Filters grades submitted in a specific week of the semester.

Matti – User Authentication and Profile Management

loginUser(credentials) – Handles secure login for students and teachers. getUserRole(userId) – Identifies user type (teacher or student). updateUserProfile(userId, updates) – Allows users to edit their profile information.

Tidjani – Grade Calculation Functions

calculateAverage(grades) – Calculates the average score from a list of grades. calculateWeightedAverage(grades, weights) – Computes a weighted average for subjects with different importance levels. getStudentRanking(classId) – (Optional) Ranks students based on their performance.

Organization Summary

Each module and function in the library follows consistent naming conventions and detailed documentation. library_name.py serves as the main library containing all core functions. utils.py may store shared helpers or validation functions. docs/function_reference.md provides detailed documentation and parameters for each function. examples/demo_script.py includes practical examples to demonstrate functionality.

Function Example:

from src.library_name import filter_by_assignment_type

grades = [ {'name': 'Alex', 'assignment_type': 'quiz', 'score': 85}, {'name': 'Maria', 'assignment_type': 'exam', 'score': 92}, {'name': 'Chris', 'assignment_type': 'quiz', 'score': 78} ]

filtered = filter_by_assignment_type(grades, 'quiz') print(filtered) Output: [{'name': 'Alex', 'assignment_type': 'quiz', 'score': 85}, {'name': 'Chris', 'assignment_type': 'quiz', 'score': 78}]

#Guidline for Team Members

To ensure consistency and collaboration, all team members should follow these contribution standards:

Branching and Workflow
Create a new branch for each feature, fix, or enhancement.
When finished, submit a pull request (PR) for review.
Commit Messages
Use clear and descriptive messages summarizing your changes. Example:

git commit -m "Added filter_by_assignment_type function and unit tests"
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

PROJECT 3

               ┌────────────────────────┐
               │        User (ABC)       │
               │  + user_id              │
               │  + name                 │
               │  + email                │
               │  + login()              │
               │  + logout()             │
               │  + dashboard() [abstract│
               └───────────┬────────────┘
                           │
   ┌───────────────────────┴────────────────────────┐
   │                                                │
┌───────────────┐ ┌────────────────┐ │ Student │ │ Teacher │ │ + classes │ │ + teaches │ │ + grades │ │ + add_grade() │ │ + view_grades │ │ + update_grade │ └───────────────┘ └────────────────┘

                 ┌────────────────────────────────┐
                 │    Assignment (ABC)             │
                 │ + name                          │
                 │ + points                        │
                 │ + max_points                    │
                 │ + calculate_percentage() [abs]  │
                 └──────────────┬─────────────────┘
                                │
 ┌──────────────────────────────┼────────────────────────────┐
 │                              │                            │
┌───────────────┐ ┌─────────────────┐ ┌─────────────────┐ │ Homework │ │ Quiz │ │ Exam │ │ + fixed weight│ │ + penalty rule │ │ + curved scores │ └───────────────┘ └─────────────────┘ └─────────────────┘

Polymorphism in the Project

Polymorphism allows the same function call to produce different behavior depending on the object type.

Example 1 — Dashboards def show_dashboard(user: User): user.dashboard() # calls Student or Teacher implementation automatically

If the object is a Student, it displays enrolled classes and current grades. If it is a Teacher, it displays course roster and grading statistics. The function call stays the same; the implementation varies by subclass.

Example 2 — Grade Calculations for assignment in student.assignments: percent = assignment.calculate_percentage()

The loop does not need to know whether the assignment is Homework, Quiz, or Exam. Polymorphism ensures each subclass applies its own rules:

Homework returns a normal percentage

Quiz may apply a late penalty

Exam may apply a grade curve

Benefits of Inheritance in This System

Without inheritance, Student and Teacher would each require their own login logic, dashboard code, session management, and shared validation. With inheritance:

Shared behavior is placed once in the User base class

Student and Teacher reuse shared functions and extend only where necessary

New user roles (Admin, Parent, Counselor, etc.) can be added by creating new subclasses and implementing the dashboard method

This reduces duplicated code, increases scalability, and enforces consistent behavior among all user types.

Usage Examples Demonstrating Inheritance and Polymorphism Adding Grades teacher = Teacher("t101", "Dr. Reed", "reed@example.com") student = Student("s300", "Ava Chen", "ava@example.com") assignment = Exam("Exam 1", 86, 100)

teacher.add_grade(student, assignment)

The system uses composition to store the grade inside the student object. Polymorphism ensures the correct percentage calculation for an Exam (curved) rather than a Quiz or Homework.

Displaying Dashboards user = login("s300") user.dashboard()

Outcome depends on the concrete object type:

If the user is a Student, grade breakdown is shown

If the user is a Teacher, course and grading statistics are shown

The caller does not need to know the subclass type.

Filtering Grades high_scores = filter_by_score_range(student.get_all_grades(), 90, 100)

The filter works regardless of whether the grades came from Homework, Quiz, or Exam objects, enabling polymorphic analytics.

Summary of OOP Requirements Concept Location in the System Inheritance User → Student / Teacher, Assignment → Homework / Quiz / Exam Abstract Classes User and Assignment define abstract methods that must be overridden Polymorphism dashboard() and calculate_percentage() execute different logic depending on object type Composition Students contain assignments and grades rather than inheriting from Assignment Encapsulation Grade modification can only occur through Teacher-validated methods

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

[[Link to presentation video - TBD]

](https://youtu.be/pN7FpXOSvrs)

## License

This project was created for INST326 at the University of Maryland.
