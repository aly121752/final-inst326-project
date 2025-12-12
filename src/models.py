"""
Core domain models for the Student Gradebook System.

This module contains all the core classes:
- AbstractAssignment, Homework, Quiz, Project, Exam
- Student, Teacher
- Course, Gradebook
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


# =============================================================================
# ASSIGNMENT CLASSES (Inheritance + Polymorphism)
# =============================================================================

class AbstractAssignment(ABC):
    """Abstract base class for all assignment types."""
    
    def __init__(self, name: str, points: float, max_points: float, week: int = 1):
        if not name.strip():
            raise ValueError("Assignment name cannot be empty")
        if max_points <= 0:
            raise ValueError("max_points must be positive")
        if points < 0:
            raise ValueError("points cannot be negative")
            
        self._name = name
        self._points = float(points)
        self._max_points = float(max_points)
        self._week = week
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def points(self) -> float:
        return self._points
    
    @points.setter
    def points(self, value: float):
        if value < 0:
            raise ValueError("points cannot be negative")
        self._points = float(value)
    
    @property
    def max_points(self) -> float:
        return self._max_points
    
    @max_points.setter
    def max_points(self, value: float):
        if value <= 0:
            raise ValueError("max_points must be positive")
        self._max_points = float(value)
    
    @property
    def week(self) -> int:
        return self._week
    
    @abstractmethod
    def calculate_percentage(self) -> float:
        """Calculate the percentage score. Each subclass implements differently."""
        pass
    
    def update(self, points: float, max_points: float):
        """Update the assignment scores."""
        self.points = points
        self.max_points = max_points
    
    def to_dict(self) -> Dict:
        """Convert assignment to dictionary for serialization."""
        return {
            "type": self.__class__.__name__,
            "name": self._name,
            "points": self._points,
            "max_points": self._max_points,
            "week": self._week
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AbstractAssignment':
        """Create assignment from dictionary. Factory method."""
        assignment_types = {
            "Homework": Homework,
            "Quiz": Quiz,
            "Project": Project,
            "Exam": Exam
        }
        atype = data.get("type", "Homework")
        klass = assignment_types.get(atype, Homework)
        return klass(
            name=data["name"],
            points=data["points"],
            max_points=data["max_points"],
            week=data.get("week", 1)
        )
    
    def __str__(self):
        return f"{self._name}: {self._points}/{self._max_points} ({self.calculate_percentage():.1f}%)"
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self._name}', {self._points}, {self._max_points})"


class Homework(AbstractAssignment):
    """Homework - standard percentage calculation."""
    
    def calculate_percentage(self) -> float:
        return (self._points / self._max_points) * 100


class Quiz(AbstractAssignment):
    """Quiz - weighted at 1.2x, capped at 100%."""
    
    def calculate_percentage(self) -> float:
        base = self._points / self._max_points
        return min(base * 1.2 * 100, 100)


class Project(AbstractAssignment):
    """Project - weighted at 0.9x (harder assignments)."""
    
    def calculate_percentage(self) -> float:
        return (self._points / self._max_points) * 0.9 * 100


class Exam(AbstractAssignment):
    """Exam - standard percentage calculation."""
    
    def calculate_percentage(self) -> float:
        return (self._points / self._max_points) * 100


# =============================================================================
# STUDENT CLASS
# =============================================================================

class Student:
    """
    Represents a student with enrolled classes and grades.
    Uses composition - a student HAS classes and assignments.
    """
    
    def __init__(self, student_id: str, name: str, major: str = "Undeclared"):
        if not student_id.strip():
            raise ValueError("student_id cannot be empty")
        if not name.strip():
            raise ValueError("name cannot be empty")
        
        self._student_id = student_id
        self._name = name
        self._major = major
        self._classes: set = set()
        self._grades: Dict[str, Dict[str, AbstractAssignment]] = {}
    
    @property
    def student_id(self) -> str:
        return self._student_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def major(self) -> str:
        return self._major
    
    @major.setter
    def major(self, value: str):
        self._major = value
    
    @property
    def classes(self) -> set:
        return self._classes.copy()
    
    @property
    def grades(self) -> Dict[str, Dict[str, AbstractAssignment]]:
        return self._grades
    
    def enroll(self, class_name: str):
        """Enroll student in a class."""
        self._classes.add(class_name)
        if class_name not in self._grades:
            self._grades[class_name] = {}
    
    def drop(self, class_name: str):
        """Drop a class."""
        self._classes.discard(class_name)
        if class_name in self._grades:
            del self._grades[class_name]
    
    def add_assignment(self, class_name: str, assignment: AbstractAssignment):
        """Add an assignment grade for a class."""
        if class_name not in self._classes:
            raise KeyError(f"{self._name} is not enrolled in {class_name}")
        self._grades[class_name][assignment.name] = assignment
    
    def update_assignment(self, class_name: str, assignment_name: str, 
                          new_points: float, new_max_points: float):
        """Update an existing assignment's scores."""
        if class_name not in self._grades:
            raise KeyError(f"No grades found for {class_name}")
        if assignment_name not in self._grades[class_name]:
            raise KeyError(f"Assignment '{assignment_name}' not found")
        self._grades[class_name][assignment_name].update(new_points, new_max_points)
    
    def delete_assignment(self, class_name: str, assignment_name: str):
        """Delete an assignment."""
        if class_name not in self._grades:
            raise KeyError(f"No grades found for {class_name}")
        if assignment_name not in self._grades[class_name]:
            raise KeyError(f"Assignment '{assignment_name}' not found")
        del self._grades[class_name][assignment_name]
    
    def get_class_average(self, class_name: str) -> Optional[float]:
        """Calculate average percentage for a class."""
        if class_name not in self._grades or not self._grades[class_name]:
            return None
        assignments = self._grades[class_name].values()
        total = sum(a.calculate_percentage() for a in assignments)
        return round(total / len(assignments), 2)
    
    def get_overall_average(self) -> Optional[float]:
        """Calculate overall average across all classes."""
        all_assignments = []
        for class_grades in self._grades.values():
            all_assignments.extend(class_grades.values())
        if not all_assignments:
            return None
        total = sum(a.calculate_percentage() for a in all_assignments)
        return round(total / len(all_assignments), 2)
    
    def to_dict(self) -> Dict:
        """Convert student to dictionary for serialization."""
        grades_dict = {}
        for class_name, assignments in self._grades.items():
            grades_dict[class_name] = {
                name: assign.to_dict() for name, assign in assignments.items()
            }
        return {
            "student_id": self._student_id,
            "name": self._name,
            "major": self._major,
            "classes": list(self._classes),
            "grades": grades_dict
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Student':
        """Create student from dictionary."""
        student = cls(
            student_id=data["student_id"],
            name=data["name"],
            major=data.get("major", "Undeclared")
        )
        for class_name in data.get("classes", []):
            student.enroll(class_name)
        
        for class_name, assignments in data.get("grades", {}).items():
            if class_name not in student._classes:
                student.enroll(class_name)
            for assign_data in assignments.values():
                assignment = AbstractAssignment.from_dict(assign_data)
                student._grades[class_name][assignment.name] = assignment
        
        return student
    
    def __str__(self):
        avg = self.get_overall_average()
        avg_str = f"{avg:.1f}%" if avg else "N/A"
        return f"{self._name} ({self._student_id}) - {self._major} - Avg: {avg_str}"
    
    def __repr__(self):
        return f"Student('{self._student_id}', '{self._name}')"


# =============================================================================
# TEACHER CLASS
# =============================================================================

class Teacher:
    """Represents a teacher who manages courses and grades students."""
    
    def __init__(self, teacher_id: str, name: str, department: str):
        if not teacher_id.strip():
            raise ValueError("teacher_id cannot be empty")
        if not name.strip():
            raise ValueError("name cannot be empty")
        if not department.strip():
            raise ValueError("department cannot be empty")
        
        self._teacher_id = teacher_id
        self._name = name
        self._department = department
        self._courses_taught: List[str] = []
    
    @property
    def teacher_id(self) -> str:
        return self._teacher_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def department(self) -> str:
        return self._department
    
    @property
    def courses_taught(self) -> List[str]:
        return self._courses_taught.copy()
    
    def add_course(self, course_code: str):
        """Add a course to teaching load."""
        if course_code not in self._courses_taught:
            self._courses_taught.append(course_code)
    
    def remove_course(self, course_code: str):
        """Remove a course from teaching load."""
        if course_code in self._courses_taught:
            self._courses_taught.remove(course_code)
    
    def to_dict(self) -> Dict:
        """Convert teacher to dictionary for serialization."""
        return {
            "teacher_id": self._teacher_id,
            "name": self._name,
            "department": self._department,
            "courses_taught": self._courses_taught
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Teacher':
        """Create teacher from dictionary."""
        teacher = cls(
            teacher_id=data["teacher_id"],
            name=data["name"],
            department=data["department"]
        )
        for course in data.get("courses_taught", []):
            teacher.add_course(course)
        return teacher
    
    def __str__(self):
        return f"{self._name} ({self._department}) - Teaching: {', '.join(self._courses_taught) or 'None'}"
    
    def __repr__(self):
        return f"Teacher('{self._teacher_id}', '{self._name}')"


# =============================================================================
# GRADEBOOK CLASS (Composition)
# =============================================================================

class Gradebook:
    """
    Central gradebook that manages all students and their grades.
    Demonstrates composition - Gradebook HAS students.
    """
    
    def __init__(self):
        self._students: Dict[str, Student] = {}
        self._teachers: Dict[str, Teacher] = {}
    
    @property
    def students(self) -> Dict[str, Student]:
        return self._students
    
    @property
    def teachers(self) -> Dict[str, Teacher]:
        return self._teachers
    
    def add_student(self, student: Student):
        """Add a student to the gradebook."""
        self._students[student.student_id] = student
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """Get a student by ID."""
        return self._students.get(student_id)
    
    def remove_student(self, student_id: str):
        """Remove a student from the gradebook."""
        if student_id in self._students:
            del self._students[student_id]
    
    def add_teacher(self, teacher: Teacher):
        """Add a teacher to the gradebook."""
        self._teachers[teacher.teacher_id] = teacher
    
    def get_teacher(self, teacher_id: str) -> Optional[Teacher]:
        """Get a teacher by ID."""
        return self._teachers.get(teacher_id)
    
    def add_grade(self, student_id: str, class_name: str, assignment: AbstractAssignment):
        """Add a grade for a student. Polymorphic - accepts any assignment type."""
        if student_id not in self._students:
            raise KeyError(f"Student '{student_id}' not found")
        
        student = self._students[student_id]
        if class_name not in student.classes:
            raise KeyError(f"{student.name} is not enrolled in {class_name}")
        
        student.add_assignment(class_name, assignment)
    
    def update_grade(self, student_id: str, class_name: str, 
                     assignment_name: str, new_points: float, new_max_points: float):
        """Update an existing grade."""
        if student_id not in self._students:
            raise KeyError(f"Student '{student_id}' not found")
        self._students[student_id].update_assignment(
            class_name, assignment_name, new_points, new_max_points
        )
    
    def delete_grade(self, student_id: str, class_name: str, assignment_name: str):
        """Delete a grade."""
        if student_id not in self._students:
            raise KeyError(f"Student '{student_id}' not found")
        self._students[student_id].delete_assignment(class_name, assignment_name)
    
    def get_class_roster(self, class_name: str) -> List[Student]:
        """Get all students enrolled in a class."""
        return [s for s in self._students.values() if class_name in s.classes]
    
    def get_class_average(self, class_name: str) -> Optional[float]:
        """Calculate average grade across all students in a class."""
        students = self.get_class_roster(class_name)
        if not students:
            return None
        averages = [s.get_class_average(class_name) for s in students]
        valid_averages = [a for a in averages if a is not None]
        if not valid_averages:
            return None
        return round(sum(valid_averages) / len(valid_averages), 2)
    
    def to_dict(self) -> Dict:
        """Convert gradebook to dictionary for serialization."""
        return {
            "students": {sid: s.to_dict() for sid, s in self._students.items()},
            "teachers": {tid: t.to_dict() for tid, t in self._teachers.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Gradebook':
        """Create gradebook from dictionary."""
        gradebook = cls()
        for student_data in data.get("students", {}).values():
            student = Student.from_dict(student_data)
            gradebook.add_student(student)
        for teacher_data in data.get("teachers", {}).values():
            teacher = Teacher.from_dict(teacher_data)
            gradebook.add_teacher(teacher)
        return gradebook
    
    def __str__(self):
        return f"Gradebook: {len(self._students)} students, {len(self._teachers)} teachers"
    
    def __repr__(self):
        return f"Gradebook(students={len(self._students)}, teachers={len(self._teachers)})"

