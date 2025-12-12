"""
Student Gradebook System

A complete gradebook management system with:
- Student and Teacher management
- Grade tracking with multiple assignment types
- Data persistence (JSON/CSV)
- Grade filtering and analysis
"""

from .models import (
    AbstractAssignment, Homework, Quiz, Project, Exam,
    Student, Teacher, Gradebook
)
from .filters import (
    GradeFilter, AssignmentTypeFilter, LateSubmissionFilter,
    ScoreRangeFilter, StudentNameFilter, WeekFilter, PassingScoreFilter,
    FilterManager,
    filter_by_assignment_type, filter_late_submissions,
    filter_by_score_range, filter_by_student_name, filter_by_week
)
from .persistence import DataStore

__all__ = [
    # Models
    'AbstractAssignment', 'Homework', 'Quiz', 'Project', 'Exam',
    'Student', 'Teacher', 'Gradebook',
    # Filters
    'GradeFilter', 'AssignmentTypeFilter', 'LateSubmissionFilter',
    'ScoreRangeFilter', 'StudentNameFilter', 'WeekFilter', 'PassingScoreFilter',
    'FilterManager',
    'filter_by_assignment_type', 'filter_late_submissions',
    'filter_by_score_range', 'filter_by_student_name', 'filter_by_week',
    # Persistence
    'DataStore'
]

