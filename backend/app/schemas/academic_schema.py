from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class CourseInfo(BaseModel):
    code: str
    name: str
    credits: int
    semester: int
    career_tags: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class EnrollmentResponse(BaseModel):
    id: int
    course: CourseInfo
    semester_taken: int
    grade: Optional[str] = None
    status: str
    model_config = ConfigDict(from_attributes=True)


class StudentProfileResponse(BaseModel):
    id: int
    roll_number: str
    full_name: str
    current_semester: int
    cgpa: float
    backlogs: int
    career_goal: Optional[str] = None
    is_at_risk: bool
    department_name: str
    enrollments: List[EnrollmentResponse]
    model_config = ConfigDict(from_attributes=True)


class CourseRecommendation(BaseModel):
    code: str
    name: str
    reason: str
    career_relevance: str


class CareerPathResponse(BaseModel):
    path_title: str
    skill_gaps: List[str]
    action_steps: List[str]
    outlook: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    student_id: Optional[int] = None


class ChatResponse(BaseModel):
    content: str
    tool_calls: List[dict] = []