from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
import json
import random
import os
import httpx
import base64
import io
import re
import math
from collections import Counter
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_password_hash
from passlib.hash import sha256_crypt
from app.models.user import User, UserRole, UserStatus
from app.models.academic import (
    StudentProfile, Department, Course, CourseEnrollment,
    ResumeChunk, ChatMessage
)
from app.schemas.academic_schema import ChatRequest

router = APIRouter(prefix="/academic", tags=["academic"])

STUDENT_NAMES = [
    "Aarav Sharma", "Priya Patel", "Rohan Mehta", "Ananya Singh", "Vikram Nair",
    "Sneha Reddy", "Arjun Kumar", "Divya Iyer", "Karan Malhotra", "Pooja Gupta",
    "Rahul Verma", "Neha Joshi", "Amit Choudhary", "Riya Desai", "Siddharth Rao",
    "Kavya Menon", "Ishaan Agarwal", "Shreya Banerjee", "Varun Tiwari", "Aisha Khan",
    "Dev Pandey", "Meera Nambiar", "Harsh Saxena", "Tanvi Bose", "Nikhil Pillai",
    "Aditi Murthy", "Yash Sinha", "Pallavi Ghosh", "Ravi Kulkarni", "Simran Sethi",
    "Akash Jain", "Deepika Mishra", "Sameer Patil", "Kritika Bhatt", "Abhinav Yadav",
    "Nandini Chatterjee", "Pranav Dubey", "Swati Kapoor", "Mohit Lal", "Anika Rajput",
    "Tushar Bajaj", "Lavanya Krishnan", "Gaurav Dixit", "Shruti Venkat", "Parth Shah",
    "Mansi Oberoi", "Ayush Shukla", "Preeti Nair", "Shivam Goel", "Natasha Mathur",
    "Kabir Das", "Isha Thakur", "Rohit Chauhan", "Anjali Hegde", "Suresh Pillai",
    "Poonam Rao", "Nitin Bhargava", "Sonali Tripathi", "Aditya Sood", "Ritika Pandey"
]

# ─── TF-IDF RAG ───────────────────────────────────────────────────────────────

def tokenize(text: str) -> list[str]:
    """Simple tokenizer — lowercase, remove punctuation, split on spaces."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    # Remove very common stop words
    stop_words = {'the','a','an','and','or','but','in','on','at','to','for',
                  'of','with','by','from','is','was','are','were','be','been',
                  'have','has','had','do','does','did','will','would','could',
                  'should','may','might','i','you','he','she','it','we','they',
                  'my','your','his','her','its','our','their','this','that','which'}
    return [t for t in tokens if t not in stop_words and len(t) > 2]

def compute_tfidf(chunk_tokens: list[str], all_chunks_tokens: list[list[str]]) -> dict:
    """Compute TF-IDF vector for a chunk given all chunks."""
    tf = Counter(chunk_tokens)
    total = len(chunk_tokens) or 1
    tf_norm = {word: count / total for word, count in tf.items()}

    # IDF: how rare is this word across all chunks
    N = len(all_chunks_tokens) or 1
    idf = {}
    all_words = set(chunk_tokens)
    for word in all_words:
        doc_count = sum(1 for tokens in all_chunks_tokens if word in tokens)
        idf[word] = math.log((N + 1) / (doc_count + 1)) + 1

    return {word: tf_norm[word] * idf[word] for word in all_words}

def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Compute cosine similarity between two TF-IDF vectors."""
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0.0
    dot = sum(vec_a[w] * vec_b[w] for w in common)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

# ─── Groq helpers ─────────────────────────────────────────────────────────────

def _groq_headers():
    key = (os.getenv("GROQ_API_KEY") or "").strip()
    if not key:
        raise ValueError("GROQ_API_KEY not configured")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

def _model():
    return (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()

async def groq_complete(messages: list, tools: list = None, temperature: float = 0.3) -> dict:
    payload = {"model": _model(), "messages": messages, "temperature": temperature}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=_groq_headers(), json=payload
        )
        r.raise_for_status()
        return r.json()

# ─── Tool implementations ──────────────────────────────────────────────────────

async def tool_get_student_profile(student_id: int, db: AsyncSession) -> dict:
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.id == student_id)
        .options(joinedload(StudentProfile.department),
                 joinedload(StudentProfile.enrollments).joinedload(CourseEnrollment.course))
    )
    s = result.unique().scalar_one_or_none()
    if not s:
        return {"error": "Student not found"}
    return {
        "id": s.id, "name": s.full_name, "roll": s.roll_number,
        "department": s.department.name, "semester": s.current_semester,
        "cgpa": s.cgpa, "backlogs": s.backlogs, "career_goal": s.career_goal,
        "is_at_risk": s.is_at_risk,
        "cgpa_level": (
            "excellent" if s.cgpa >= 8.5 else
            "good" if s.cgpa >= 7.5 else
            "average" if s.cgpa >= 6.5 else
            "below average" if s.cgpa >= 6.0 else "poor"
        ),
        "enrollments": [
            {"course": e.course.name, "code": e.course.code,
             "grade": e.grade, "status": e.status, "credits": e.course.credits}
            for e in s.enrollments
        ]
    }

async def tool_get_available_courses(student_id: int, db: AsyncSession) -> dict:
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.id == student_id)
        .options(joinedload(StudentProfile.enrollments))
    )
    s = result.unique().scalar_one_or_none()
    if not s:
        return {"error": "Student not found"}
    next_sem = s.current_semester + 1
    courses_res = await db.execute(select(Course).where(Course.department_id == s.department_id))
    all_courses = courses_res.scalars().all()
    completed_ids = {e.course_id for e in s.enrollments if e.status == "completed"}
    available = [
        {"code": c.code, "name": c.name, "semester": c.semester,
         "credits": c.credits, "career_tags": c.career_tags, "prerequisites": c.prerequisites}
        for c in all_courses if c.id not in completed_ids
    ]
    return {"next_semester": next_sem, "available_courses": available}

async def tool_search_resume(student_id: int, query: str, db: AsyncSession) -> dict:
    """TF-IDF based semantic search over resume chunks."""
    result = await db.execute(
        select(ResumeChunk).where(ResumeChunk.student_id == student_id)
        .order_by(ResumeChunk.chunk_index)
    )
    chunks = result.scalars().all()
    if not chunks:
        return {"found": False, "message": "No resume uploaded for this student. Ask them to upload their resume PDF in the chat."}

    query_tokens = tokenize(query)
    if not query_tokens:
        return {"found": True, "relevant_sections": [chunks[0].content], "total_chunks": len(chunks)}

    # Load stored TF-IDF vectors
    scored = []
    for chunk in chunks:
        if chunk.tfidf_vector:
            chunk_vec = json.loads(chunk.tfidf_vector)
        else:
            # Fallback: compute on the fly
            chunk_tokens = tokenize(chunk.content)
            all_tokens = [tokenize(c.content) for c in chunks]
            chunk_vec = compute_tfidf(chunk_tokens, all_tokens)

        # Build query vector against this chunk's vocabulary
        query_tf = Counter(query_tokens)
        query_total = len(query_tokens)
        query_vec = {w: (query_tf[w] / query_total) * chunk_vec.get(w, 0)
                     for w in query_tokens if w in chunk_vec}

        score = cosine_similarity(query_vec, chunk_vec)
        scored.append((score, chunk.content))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [content for score, content in scored[:3] if score > 0]

    if not top:
        top = [chunks[0].content]

    return {
        "found": True,
        "relevant_sections": top,
        "total_chunks": len(chunks),
        "search_method": "TF-IDF cosine similarity"
    }

async def tool_get_chat_history(student_id: int, db: AsyncSession) -> dict:
    """Get the last 6 messages from previous sessions."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.student_id == student_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(6)
    )
    messages = result.scalars().all()
    messages.reverse()
    if not messages:
        return {"history": [], "message": "No previous conversations"}
    return {
        "history": [{"role": m.role, "content": m.content[:300]} for m in messages],
        "message": f"Last {len(messages)} messages from previous sessions"
    }

# ─── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_student_profile",
            "description": "Get complete academic profile — CGPA, courses, grades, backlogs, career goal. Call this first.",
            "parameters": {
                "type": "object",
                "properties": {"student_id": {"type": "integer"}},
                "required": ["student_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_courses",
            "description": "Get courses available for the student in upcoming semesters.",
            "parameters": {
                "type": "object",
                "properties": {"student_id": {"type": "integer"}},
                "required": ["student_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_resume",
            "description": "Search the student's resume using semantic TF-IDF search. Call when asked about resume, skills, experience, or gap analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "integer"},
                    "query": {"type": "string", "description": "What to search for in the resume"}
                },
                "required": ["student_id", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_chat_history",
            "description": "Get previous conversation history with this student. Call this to maintain continuity across sessions.",
            "parameters": {
                "type": "object",
                "properties": {"student_id": {"type": "integer"}},
                "required": ["student_id"]
            }
        }
    }
]

# ─── Agentic loop ──────────────────────────────────────────────────────────────

async def run_agent(messages: list, student_id: int, db: AsyncSession) -> str:
    system = """You are the Atlas University Academic Advisor — an intelligent agent with memory.

You have tools to look up student data. Always use them — never guess or assume.

Rules:
- Call get_student_profile first before giving any academic advice
- Call get_chat_history to recall what you discussed before with this student
- Call search_resume when asked about resume, skills, experience, or gaps
- Call get_available_courses when asked about what to study next
- Be honest about CGPA: below 6 = poor, 6-6.5 = needs improvement, 6.5-7.5 = average, 7.5-8.5 = good, above 8.5 = excellent
- Reference previous conversations naturally — "Last time we discussed..."
- Give specific actionable advice based on real data only"""

    agent_messages = [{"role": "system", "content": system}] + messages

    max_iterations = 6
    for _ in range(max_iterations):
        response = await groq_complete(agent_messages, tools=TOOLS, temperature=0.4)
        choice = response["choices"][0]
        message = choice["message"]

        if not message.get("tool_calls"):
            return message.get("content", "I could not generate a response.")

        agent_messages.append(message)

        for tool_call in message["tool_calls"]:
            fn_name = tool_call["function"]["name"]
            fn_args = json.loads(tool_call["function"]["arguments"])
            tool_call_id = tool_call["id"]

            if fn_name == "get_student_profile":
                result = await tool_get_student_profile(fn_args["student_id"], db)
            elif fn_name == "get_available_courses":
                result = await tool_get_available_courses(fn_args["student_id"], db)
            elif fn_name == "search_resume":
                result = await tool_search_resume(fn_args["student_id"], fn_args["query"], db)
            elif fn_name == "get_chat_history":
                result = await tool_get_chat_history(fn_args["student_id"], db)
            else:
                result = {"error": f"Unknown tool: {fn_name}"}

            agent_messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(result)
            })

    return "I was unable to complete the analysis. Please try again."

# ─── API endpoints ─────────────────────────────────────────────────────────────

@router.get("/students")
async def get_all_students(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudentProfile).options(joinedload(StudentProfile.department)))
    students = result.unique().scalars().all()
    return [{"id": s.id, "name": s.full_name, "roll": s.roll_number, "dept": s.department.name} for s in students]


@router.get("/profile/{student_id}")
async def get_student_profile_endpoint(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.id == student_id)
        .options(joinedload(StudentProfile.department),
                 joinedload(StudentProfile.enrollments).joinedload(CourseEnrollment.course))
    )
    profile = result.unique().scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    profile.department_name = profile.department.name
    return profile


@router.get("/recommendations/{student_id}")
async def get_recommendations(student_id: int, db: AsyncSession = Depends(get_db)):
    profile = await tool_get_student_profile(student_id, db)
    courses = await tool_get_available_courses(student_id, db)
    messages = [
        {"role": "user", "content": f"Recommend exactly 3 courses. Return ONLY a JSON array: [{{'code':'...','name':'...','reason':'...','career_relevance':'...'}}]\n\nProfile: {json.dumps(profile)}\nAvailable: {json.dumps(courses)}"}
    ]
    try:
        resp = await groq_complete(messages, temperature=0.3)
        raw = resp["choices"][0]["message"]["content"]
        clean = raw.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\[.*\]', clean, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(clean)
    except Exception:
        avail = courses.get("available_courses", [])
        return [{"code": c["code"], "name": c["name"], "reason": "Recommended for your profile", "career_relevance": c.get("career_tags", "Core")} for c in avail[:3]]


@router.get("/career-path/{student_id}")
async def get_career_path(student_id: int, db: AsyncSession = Depends(get_db)):
    profile = await tool_get_student_profile(student_id, db)
    messages = [
        {"role": "user", "content": f"Suggest a career path. Return ONLY JSON: {{\"path_title\":\"...\",\"skill_gaps\":[\"...\"],\"action_steps\":[\"...\"],\"outlook\":\"...\"}}\n\nProfile: {json.dumps(profile)}"}
    ]
    try:
        resp = await groq_complete(messages, temperature=0.3)
        raw = resp["choices"][0]["message"]["content"]
        clean = raw.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\{.*\}', clean, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(clean)
    except Exception:
        return {
            "path_title": f"{profile.get('career_goal', 'Professional')} Track",
            "skill_gaps": ["Industry experience", "Certifications"],
            "action_steps": ["Focus on current semester", "Apply for internships", "Build projects"],
            "outlook": "Strong market demand"
        }


@router.post("/chat")
async def academic_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not req.student_id:
        raise HTTPException(status_code=400, detail="student_id required")

    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    messages_with_context = messages[:-1] + [
        {"role": "user", "content": f"[Student ID: {req.student_id}] {messages[-1]['content']}"}
    ]

    try:
        content = await run_agent(messages_with_context, req.student_id, db)

        # Save this exchange to memory
        user_msg = messages[-1]["content"]
        db.add(ChatMessage(
            student_id=req.student_id,
            role="user",
            content=user_msg,
            created_at=datetime.now(timezone.utc)
        ))
        db.add(ChatMessage(
            student_id=req.student_id,
            role="assistant",
            content=content,
            created_at=datetime.now(timezone.utc)
        ))
        await db.commit()

        return {"content": content, "tool_calls": []}
    except Exception as e:
        return {"content": f"I'm having trouble right now. Please try again. ({str(e)})", "tool_calls": []}


@router.post("/student-login")
async def student_login(body: dict, db: AsyncSession = Depends(get_db)):
    email = body.get("email", "").lower().strip()
    password = body.get("password", "")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    user_result = await db.execute(select(User).where(User.email == email))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    try:
        if not sha256_crypt.verify(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
        .options(joinedload(StudentProfile.department),
                 joinedload(StudentProfile.enrollments).joinedload(CourseEnrollment.course))
    )
    profile = result.unique().scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    profile.department_name = profile.department.name
    return profile


@router.post("/upload-resume/{student_id}")
async def upload_resume(student_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    pdf_base64 = body.get("pdf_base64", "")
    if not pdf_base64:
        raise HTTPException(status_code=400, detail="pdf_base64 required")

    try:
        pdf_bytes = base64.b64decode(pdf_base64)
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            full_text = " ".join([page.extract_text() or "" for page in reader.pages])
        except ImportError:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            full_text = " ".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")

    if not full_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # Delete old chunks
    old = await db.execute(select(ResumeChunk).where(ResumeChunk.student_id == student_id))
    for chunk in old.scalars().all():
        await db.delete(chunk)

    # Chunk the text
    words = full_text.split()
    chunk_size = 300
    overlap = 50
    raw_chunks = []
    i = 0
    while i < len(words):
        raw_chunks.append(" ".join(words[i:i + chunk_size]))
        i += chunk_size - overlap

    # Compute TF-IDF vectors for all chunks
    all_tokens = [tokenize(chunk) for chunk in raw_chunks]
    chunk_vectors = []
    for idx, (chunk_text, tokens) in enumerate(zip(raw_chunks, all_tokens)):
        vec = compute_tfidf(tokens, all_tokens)
        chunk_vectors.append(vec)
        db.add(ResumeChunk(
            student_id=student_id,
            chunk_index=idx,
            content=chunk_text,
            tfidf_vector=json.dumps(vec)
        ))

    await db.commit()
    return {
        "message": "Resume uploaded and indexed with TF-IDF vectors",
        "chunks": len(raw_chunks),
        "words": len(words)
    }


@router.get("/chat-history/{student_id}")
async def get_chat_history_endpoint(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.student_id == student_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
    )
    messages = result.scalars().all()
    messages.reverse()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages]


@router.post("/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    count = await db.execute(select(func.count(Department.id)))
    if count.scalar() > 0:
        return {"message": "Already seeded", "status": "skipped"}

    depts = [
        Department(name="Computer Science and Engineering", code="CSE", hod_name="Dr. Alan Turing"),
        Department(name="Bachelor of Business Administration", code="BBA", hod_name="Dr. Peter Drucker"),
        Department(name="Institute of Design", code="ISDI", hod_name="Dr. Paula Scher"),
    ]
    db.add_all(depts)
    await db.flush()

    all_courses = [
        Course(code="CS201", name="Advanced Algorithms", department_id=depts[0].id, semester=2, credits=4, prerequisites=None, career_tags="software,research"),
        Course(code="CS301", name="Statistics for Computing", department_id=depts[0].id, semester=3, credits=4, prerequisites="CS201", career_tags="data-science,research"),
        Course(code="CS501", name="Mobile & Cloud Systems", department_id=depts[0].id, semester=5, credits=4, prerequisites="CS301", career_tags="software,cloud"),
        Course(code="CS601", name="Cybersecurity Fundamentals", department_id=depts[0].id, semester=6, credits=4, prerequisites="CS501", career_tags="cybersecurity,software"),
        Course(code="BM101", name="Financial Accounting", department_id=depts[1].id, semester=1, credits=4, prerequisites=None, career_tags="finance,consulting"),
        Course(code="BM201", name="Marketing Management", department_id=depts[1].id, semester=2, credits=4, prerequisites="BM101", career_tags="marketing,management"),
        Course(code="BM301", name="Organisational Behaviour", department_id=depts[1].id, semester=3, credits=4, prerequisites=None, career_tags="management,consulting"),
        Course(code="BM401", name="Business Strategy & Analytics", department_id=depts[1].id, semester=4, credits=4, prerequisites="BM201", career_tags="consulting,management"),
        Course(code="DS101", name="Typography & Visual Communication", department_id=depts[2].id, semester=1, credits=4, prerequisites=None, career_tags="design,creative"),
        Course(code="DS301", name="Motion Graphics & Animation", department_id=depts[2].id, semester=3, credits=4, prerequisites="DS101", career_tags="animation,creative"),
        Course(code="DS401", name="UX Design & Research", department_id=depts[2].id, semester=4, credits=4, prerequisites="DS101", career_tags="ux,design"),
        Course(code="DS501", name="Design Thinking & Innovation", department_id=depts[2].id, semester=5, credits=4, prerequisites="DS401", career_tags="design,ux"),
    ]
    db.add_all(all_courses)
    await db.flush()

    goals_map = {
        "CSE": ["software engineer", "data scientist", "cybersecurity analyst"],
        "BBA": ["finance analyst", "marketing manager", "consultant"],
        "ISDI": ["ux designer", "motion designer", "creative director"],
    }
    dept_assignments = (
        [(n, depts[0], "CSE") for n in STUDENT_NAMES[:25]] +
        [(n, depts[1], "BBA") for n in STUDENT_NAMES[25:45]] +
        [(n, depts[2], "ISDI") for n in STUDENT_NAMES[45:60]]
    )

    for i, (name, dept, dept_code) in enumerate(dept_assignments):
        roll = f"AU2022{dept_code}{str(i + 1).zfill(3)}"
        email = f"{roll.lower()}@atlasuniversity.edu.in"
        user = User(
            email=email,
            hashed_password=sha256_crypt.hash("student123"),
            role=UserRole.USER,
            status=UserStatus.APPROVED
        )
        db.add(user)
        await db.flush()

        sem = random.randint(2, 8)
        cgpa = round(random.uniform(5.5, 9.8), 2)
        backlogs = random.choices([0, 1, 2, 3], weights=[40, 15, 10, 5])[0]
        profile = StudentProfile(
            user_id=user.id, roll_number=roll, full_name=name,
            department_id=dept.id, current_semester=sem, cgpa=cgpa,
            backlogs=backlogs, career_goal=random.choice(goals_map[dept_code]),
            is_at_risk=(cgpa < 6.0 or backlogs >= 3),
        )
        db.add(profile)
        await db.flush()

        dept_courses = [c for c in all_courses if c.department_id == dept.id]
        for c in dept_courses:
            if c.semester < sem:
                db.add(CourseEnrollment(
                    student_id=profile.id, course_id=c.id, semester_taken=c.semester,
                    grade=random.choices(["S", "A", "B", "C", "D"], weights=[10, 30, 35, 15, 10])[0],
                    status="completed"
                ))
            elif c.semester == sem:
                db.add(CourseEnrollment(
                    student_id=profile.id, course_id=c.id,
                    semester_taken=sem, grade=None, status="ongoing"
                ))

    await db.commit()
    return {"message": "Seeded successfully", "students": 60, "courses": 12, "departments": 3}