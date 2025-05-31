from .course_viewset import CourseViewSet
from .teacher_assignment_viewset import TeacherAssignmentViewSet
from .period_viewset import PeriodViewSet
from .subject_viewset import SubjectViewSet
from .enrollment_viewset import EnrollmentViewSet
from .attendance_viewset import AttendanceViewSet
from .participation_viewset import ParticipationViewSet
from .trimester_viewset import TrimesterViewSet
from .assessment_item_viewset import AssessmentItemViewSet
from .grade_viewset import GradeViewSet


__all__ = [
    'CourseViewSet',
    'TeacherAssignmentViewSet',
    'PeriodViewSet',
    'SubjectViewSet',
    'EnrollmentViewSet',
    'AttendanceViewSet',
    'ParticipationViewSet',
    'TrimesterViewSet',
    'AssessmentItemViewSet',
    'GradeViewSet',
]