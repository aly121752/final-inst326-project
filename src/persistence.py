"""
Data persistence module for the Student Gradebook System.

Handles:
- Save/load system state to/from JSON
- Import data from CSV
- Export reports to JSON/CSV
- Error handling for file operations
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .models import Gradebook, Student, Teacher, AbstractAssignment, Homework, Quiz, Project, Exam


class DataStore:
    """
    Handles all data persistence operations.
    Uses pathlib for cross-platform file path management.
    Uses context managers for safe file operations.
    """
    
    DEFAULT_DATA_FILE = "gradebook_data.json"
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the datastore with a data directory."""
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def data_dir(self) -> Path:
        return self._data_dir
    
    # =========================================================================
    # SAVE/LOAD SYSTEM STATE (JSON)
    # =========================================================================
    
    def save_gradebook(self, gradebook: Gradebook, filename: str = None) -> Tuple[bool, str]:
        """
        Save the entire gradebook state to a JSON file.
        
        Args:
            gradebook: The Gradebook instance to save
            filename: Optional filename (defaults to DEFAULT_DATA_FILE)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        filename = filename or self.DEFAULT_DATA_FILE
        filepath = self._data_dir / filename
        
        try:
            data = gradebook.to_dict()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True, f"Gradebook saved to {filepath}"
        except (IOError, OSError) as e:
            return False, f"Error saving gradebook: {e}"
        except TypeError as e:
            return False, f"Error serializing data: {e}"
    
    def load_gradebook(self, filename: str = None) -> Tuple[Optional[Gradebook], str]:
        """
        Load gradebook state from a JSON file.
        
        Args:
            filename: Optional filename (defaults to DEFAULT_DATA_FILE)
        
        Returns:
            Tuple of (Gradebook or None, message: str)
        """
        filename = filename or self.DEFAULT_DATA_FILE
        filepath = self._data_dir / filename
        
        if not filepath.exists():
            return None, f"File not found: {filepath}"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            gradebook = Gradebook.from_dict(data)
            return gradebook, f"Gradebook loaded from {filepath}"
        except json.JSONDecodeError as e:
            return None, f"Error parsing JSON: {e}"
        except (IOError, OSError) as e:
            return None, f"Error reading file: {e}"
        except (KeyError, ValueError) as e:
            return None, f"Error in data format: {e}"
    
    # =========================================================================
    # IMPORT FROM CSV
    # =========================================================================
    
    def import_grades_from_csv(self, gradebook: Gradebook, 
                                filepath: str) -> Tuple[int, str]:
        """
        Import grades from a CSV file into the gradebook.
        
        Expected CSV format:
        student_id,student_name,class_name,assignment_name,assignment_type,points,max_points,week
        
        Args:
            gradebook: The Gradebook to add grades to
            filepath: Path to the CSV file
        
        Returns:
            Tuple of (records_imported: int, message: str)
        """
        path = Path(filepath)
        
        if not path.exists():
            return 0, f"File not found: {filepath}"
        
        imported = 0
        errors = []
        
        try:
            with open(path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        student_id = row.get('student_id', '').strip()
                        student_name = row.get('student_name', '').strip()
                        class_name = row.get('class_name', '').strip()
                        assignment_name = row.get('assignment_name', '').strip()
                        assignment_type = row.get('assignment_type', 'homework').strip().lower()
                        points = float(row.get('points', 0))
                        max_points = float(row.get('max_points', 100))
                        week = int(row.get('week', 1))
                        
                        if not all([student_id, student_name, class_name, assignment_name]):
                            errors.append(f"Row {row_num}: Missing required fields")
                            continue
                        
                        # Create or get student
                        student = gradebook.get_student(student_id)
                        if not student:
                            student = Student(student_id, student_name)
                            gradebook.add_student(student)
                        
                        # Enroll in class if not already
                        if class_name not in student.classes:
                            student.enroll(class_name)
                        
                        # Create appropriate assignment type
                        assignment_classes = {
                            'homework': Homework,
                            'quiz': Quiz,
                            'project': Project,
                            'exam': Exam
                        }
                        AssignmentClass = assignment_classes.get(assignment_type, Homework)
                        assignment = AssignmentClass(assignment_name, points, max_points, week)
                        
                        # Add grade
                        student.add_assignment(class_name, assignment)
                        imported += 1
                        
                    except (ValueError, KeyError) as e:
                        errors.append(f"Row {row_num}: {e}")
            
            message = f"Imported {imported} grades"
            if errors:
                message += f" with {len(errors)} errors"
            return imported, message
            
        except (IOError, OSError) as e:
            return 0, f"Error reading CSV: {e}"
    
    def import_students_from_csv(self, gradebook: Gradebook, 
                                  filepath: str) -> Tuple[int, str]:
        """
        Import students from a CSV file.
        
        Expected CSV format:
        student_id,name,major,classes (comma-separated)
        
        Returns:
            Tuple of (records_imported: int, message: str)
        """
        path = Path(filepath)
        
        if not path.exists():
            return 0, f"File not found: {filepath}"
        
        imported = 0
        
        try:
            with open(path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    student_id = row.get('student_id', '').strip()
                    name = row.get('name', '').strip()
                    major = row.get('major', 'Undeclared').strip()
                    classes_str = row.get('classes', '')
                    
                    if not student_id or not name:
                        continue
                    
                    student = Student(student_id, name, major)
                    
                    if classes_str:
                        for class_name in classes_str.split(','):
                            class_name = class_name.strip()
                            if class_name:
                                student.enroll(class_name)
                    
                    gradebook.add_student(student)
                    imported += 1
            
            return imported, f"Imported {imported} students"
            
        except (IOError, OSError) as e:
            return 0, f"Error reading CSV: {e}"
    
    # =========================================================================
    # EXPORT TO JSON/CSV
    # =========================================================================
    
    def export_grades_report(self, gradebook: Gradebook, 
                              filename: str = "grades_report.json") -> Tuple[bool, str]:
        """
        Export a grades summary report to JSON.
        
        Args:
            gradebook: The Gradebook to export from
            filename: Output filename
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        filepath = self._data_dir / filename
        
        report = {
            "summary": {
                "total_students": len(gradebook.students),
                "total_teachers": len(gradebook.teachers)
            },
            "students": []
        }
        
        for student in gradebook.students.values():
            student_report = {
                "student_id": student.student_id,
                "name": student.name,
                "major": student.major,
                "overall_average": student.get_overall_average(),
                "classes": []
            }
            
            for class_name in student.classes:
                class_avg = student.get_class_average(class_name)
                assignments = student.grades.get(class_name, {})
                
                class_report = {
                    "class_name": class_name,
                    "average": class_avg,
                    "assignment_count": len(assignments)
                }
                student_report["classes"].append(class_report)
            
            report["students"].append(student_report)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            return True, f"Report exported to {filepath}"
        except (IOError, OSError) as e:
            return False, f"Error exporting report: {e}"
    
    def export_grades_to_csv(self, gradebook: Gradebook, 
                              filename: str = "grades_export.csv") -> Tuple[bool, str]:
        """
        Export all grades to a CSV file.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        filepath = self._data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'student_id', 'student_name', 'major', 'class_name',
                    'assignment_name', 'assignment_type', 'points', 'max_points',
                    'percentage', 'week'
                ])
                
                for student in gradebook.students.values():
                    for class_name, assignments in student.grades.items():
                        for assign_name, assignment in assignments.items():
                            writer.writerow([
                                student.student_id,
                                student.name,
                                student.major,
                                class_name,
                                assignment.name,
                                assignment.__class__.__name__,
                                assignment.points,
                                assignment.max_points,
                                round(assignment.calculate_percentage(), 2),
                                assignment.week
                            ])
            
            return True, f"Grades exported to {filepath}"
        except (IOError, OSError) as e:
            return False, f"Error exporting CSV: {e}"
    
    def export_class_roster(self, gradebook: Gradebook, class_name: str,
                             filename: str = None) -> Tuple[bool, str]:
        """
        Export a class roster with grades to CSV.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        filename = filename or f"{class_name}_roster.csv"
        filepath = self._data_dir / filename
        
        students = gradebook.get_class_roster(class_name)
        
        if not students:
            return False, f"No students found in {class_name}"
        
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['student_id', 'name', 'major', 'class_average'])
                
                for student in students:
                    avg = student.get_class_average(class_name)
                    writer.writerow([
                        student.student_id,
                        student.name,
                        student.major,
                        avg if avg else 'N/A'
                    ])
            
            return True, f"Roster exported to {filepath}"
        except (IOError, OSError) as e:
            return False, f"Error exporting roster: {e}"

