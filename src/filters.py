"""
Grade filtering system using abstract base classes and polymorphism.

Provides various filters that can be composed together to filter grade data.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class GradeFilter(ABC):
    """Abstract base class for all grade filters."""
    
    @abstractmethod
    def apply(self, grades: List[Dict]) -> List[Dict]:
        """Apply filter to a grade list and return filtered list."""
        pass


class AssignmentTypeFilter(GradeFilter):
    """Filter grades by assignment type (e.g., 'quiz', 'homework', 'exam')."""
    
    def __init__(self, assignment_type: str):
        self.assignment_type = assignment_type.lower()
    
    def apply(self, grades: List[Dict]) -> List[Dict]:
        return [g for g in grades if g.get('assignment_type', '').lower() == self.assignment_type]


class LateSubmissionFilter(GradeFilter):
    """Filter to get only late submissions."""
    
    def apply(self, grades: List[Dict]) -> List[Dict]:
        return [g for g in grades if g.get('is_late', False)]


class ScoreRangeFilter(GradeFilter):
    """Filter grades within a score range."""
    
    def __init__(self, min_score: float = 0, max_score: float = 100):
        self.min_score = min_score
        self.max_score = max_score
    
    def apply(self, grades: List[Dict]) -> List[Dict]:
        return [g for g in grades if self.min_score <= g.get('score', 0) <= self.max_score]


class StudentNameFilter(GradeFilter):
    """Filter grades for a specific student (case-insensitive)."""
    
    def __init__(self, student_name: str):
        self.student_name = student_name.lower()
    
    def apply(self, grades: List[Dict]) -> List[Dict]:
        return [g for g in grades if g.get('name', '').lower() == self.student_name]


class WeekFilter(GradeFilter):
    """Filter grades by week number."""
    
    def __init__(self, week_number: int):
        self.week_number = week_number
    
    def apply(self, grades: List[Dict]) -> List[Dict]:
        return [g for g in grades if g.get('week') == self.week_number]


class PassingScoreFilter(GradeFilter):
    """Filter to get only passing grades."""
    
    def __init__(self, passing_score: float = 60):
        self.passing_score = passing_score
    
    def apply(self, grades: List[Dict]) -> List[Dict]:
        return [g for g in grades if g.get('score', 0) >= self.passing_score]


class FilterManager:
    """
    Manages and applies multiple grade filters.
    Demonstrates composition - FilterManager HAS multiple GradeFilter objects.
    """
    
    def __init__(self):
        self._filters: List[GradeFilter] = []
    
    def add_filter(self, grade_filter: GradeFilter):
        """Add a filter. Uses polymorphism - any GradeFilter subtype works."""
        self._filters.append(grade_filter)
    
    def clear_filters(self):
        """Remove all filters."""
        self._filters.clear()
    
    def apply_all(self, grades: List[Dict]) -> List[Dict]:
        """
        Apply all filters in sequence.
        Polymorphism: each filter's apply() method is called regardless of concrete type.
        """
        result = grades
        for f in self._filters:
            result = f.apply(result)
        return result


# =============================================================================
# CONVENIENCE FUNCTIONS (for simpler usage)
# =============================================================================

def filter_by_assignment_type(grades: List[Dict], assignment_type: str) -> List[Dict]:
    """Filter grades by assignment type."""
    return AssignmentTypeFilter(assignment_type).apply(grades)


def filter_late_submissions(grades: List[Dict]) -> List[Dict]:
    """Get all late submissions."""
    return LateSubmissionFilter().apply(grades)


def filter_by_score_range(grades: List[Dict], min_score: float = 0, max_score: float = 100) -> List[Dict]:
    """Filter grades within a score range."""
    return ScoreRangeFilter(min_score, max_score).apply(grades)


def filter_by_student_name(grades: List[Dict], student_name: str) -> List[Dict]:
    """Filter grades for a specific student."""
    return StudentNameFilter(student_name).apply(grades)


def filter_by_week(grades: List[Dict], week_number: int) -> List[Dict]:
    """Filter grades by week number."""
    return WeekFilter(week_number).apply(grades)

