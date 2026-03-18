from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    hod_name: Mapped[str] = mapped_column(String(255), nullable=False)
    courses: Mapped[List["Course"]] = relationship("Course", back_populates="department")
    students: Mapped[List["StudentProfile"]] = relationship("StudentProfile", back_populates="department")


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    prerequisites: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    career_tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped["Department"] = relationship("Department", back_populates="courses")
    enrollments: Mapped[List["CourseEnrollment"]] = relationship("CourseEnrollment", back_populates="course")


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    roll_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    current_semester: Mapped[int] = mapped_column(Integer, nullable=False)
    cgpa: Mapped[float] = mapped_column(Float, nullable=False)
    backlogs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    career_goal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_at_risk: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    department: Mapped["Department"] = relationship("Department", back_populates="students")
    enrollments: Mapped[List["CourseEnrollment"]] = relationship(
        "CourseEnrollment", back_populates="student", cascade="all, delete-orphan"
    )
    resume_chunks: Mapped[List["ResumeChunk"]] = relationship(
        "ResumeChunk", back_populates="student", cascade="all, delete-orphan"
    )
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="student", cascade="all, delete-orphan"
    )


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    semester_taken: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")


class ResumeChunk(Base):
    __tablename__ = "resume_chunks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # TF-IDF vector stored as JSON string
    tfidf_vector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="resume_chunks")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user or assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="chat_messages")