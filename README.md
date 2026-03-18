# Atlas AI Command Centre — Smart Academic Advisor

A university AI platform built on the Atlas AI Command Centre template. Students get personalised course recommendations, career path projections, and an agentic AI advisor that reasons over their live academic data. Supports resume upload with TF-IDF RAG, persistent memory across sessions, and tool-based agentic reasoning.

---

## 🎓 What Was Built

The **Smart Academic Advisor** is an AI agent added on top of the Atlas template. It is fully agentic — the AI has tools it calls itself to fetch live data from the database before answering. Nothing is hardcoded or pre-loaded into the AI.

### How It Works

When a student asks a question in the chat:
1. The AI reads the question
2. It **decides** which tools to call — `get_student_profile`, `get_available_courses`, `search_resume`, `get_chat_history`
3. Tools fetch live data from PostgreSQL
4. The AI reasons over the results and gives a personalised answer
5. The conversation is saved to the database for future sessions

When a student uploads a resume:
1. PDF text is extracted and split into 300-word chunks
2. TF-IDF vectors are computed for each chunk and stored in PostgreSQL
3. When the student asks about their resume, the AI calls `search_resume`
4. Cosine similarity retrieves the most relevant chunks — this is RAG

When a student returns for a new session:
1. Previous conversations are loaded from the `chat_messages` table
2. Last 6 messages are passed as context to every new message
3. The AI can reference previous discussions naturally

---

## ✨ Features

| Feature | Description |
|---|---|
| **Agentic Chat** | AI calls tools to fetch live data — never pre-loaded |
| **Persistent Memory** | Chat history stored in PostgreSQL, loaded on every new session |
| **Course Recommendations** | AI recommends next semester courses based on actual profile |
| **Career Path** | AI generates career roadmap with skill gaps and action steps |
| **Resume RAG** | PDF chunked, TF-IDF vectorised, semantically searched via cosine similarity |
| **Student Login** | Students log in with university email and password |
| **Admin View** | Staff can select any student and view their full profile |
| **At-Risk Detection** | Students with CGPA below 6 or 3+ backlogs are automatically flagged |
| **Audit Logging** | All API requests are automatically logged |
| **AI Policies** | Natural language rule engine (from base template) |
| **AI Insights** | Proactive system analysis (from base template) |

---

## 🚀 Quick Start

### Prerequisites

| Tool | Required |
|---|---|
| Docker Desktop | ✅ Yes |
| Groq API Key (free) | ✅ Yes — get one at [console.groq.com](https://console.groq.com) |

### Step 1 — Clone and set up

```bash
git clone <your-repo-url>
cd AAS
cp .env.example .env
```

### Step 2 — Add your Groq API key

Open `.env` and set:

```
GROQ_API_KEY=your_groq_key_here
```

### Step 3 — Start everything

```bash
docker compose up --build
```

Wait for:
```
backend  | Application startup complete
frontend | Ready in Xs
```

### Step 4 — Open the app

| Service | URL |
|---|---|
| 🌐 App | http://localhost:3000 |
| 📡 API Docs | http://localhost:8000/docs |

### Step 5 — Seed the database

Go to `http://localhost:3000/academic` and click **Seed Database**.

This creates 60 students across 3 departments with realistic profiles, courses, and enrollments.

### Step 6 — Log in as a student

- Email: `au2022cse001@atlasuniversity.edu.in`
- Password: `student123`

---

## 💻 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Frontend | Next.js 14 + React + TypeScript |
| Database | PostgreSQL 15 |
| AI | Groq API — LLaMA 3 (free tier) |
| RAG | TF-IDF vectorisation + cosine similarity |
| ORM | SQLAlchemy async |
| Auth | JSON-based RBAC via authz.map.json |
| Infrastructure | Docker + Docker Compose (5 containers) |

---

## 🤖 Agent Tools

The AI has 4 tools. It decides when to call them based on the question.

| Tool | What It Fetches |
|---|---|
| `get_student_profile` | CGPA, semester, department, all courses with grades, backlogs, career goal |
| `get_available_courses` | Courses in student's department not yet completed |
| `search_resume` | Relevant chunks from the student's stored resume using TF-IDF cosine similarity |
| `get_chat_history` | Last 6 messages from previous sessions for memory continuity |

---

## 🗄️ Database Schema

| Table | What It Stores |
|---|---|
| `departments` | CSE, BBA, ISDI with HOD names |
| `courses` | 12 courses with semester, credits, prerequisites, career tags |
| `student_profiles` | CGPA, semester, backlogs, career goal, at-risk flag |
| `course_enrollments` | Student-course links with grades and status |
| `resume_chunks` | Chunked resume text + TF-IDF vectors per student |
| `chat_messages` | Full conversation history per student with timestamps |
| `users` | Login credentials for all students and admin |
| `audit_logs` | Automatic log of every API request |
| `policies` | AI-generated access control policies |

---

## 📡 Academic API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/academic/students` | List all students |
| GET | `/api/academic/profile/{id}` | Full student profile |
| GET | `/api/academic/recommendations/{id}` | AI course recommendations |
| GET | `/api/academic/career-path/{id}` | AI career path projection |
| POST | `/api/academic/chat` | Agentic chat — AI calls tools internally |
| POST | `/api/academic/student-login` | Login with email + password |
| POST | `/api/academic/upload-resume/{id}` | Upload, chunk and TF-IDF index a resume PDF |
| GET | `/api/academic/chat-history/{id}` | Stored conversation history |
| POST | `/api/academic/seed` | Seed demo data |

---

## 📂 Project Structure

```
AAS/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── academic.py        ← Academic advisor agent + all endpoints
│   │   │   ├── ai.py              ← AI policies, insights, chat (template)
│   │   │   ├── admin.py           ← User management, audit logs (template)
│   │   │   └── auth.py            ← Login / register (template)
│   │   ├── models/
│   │   │   ├── academic.py        ← Department, Course, Student, Enrollment, ResumeChunk, ChatMessage
│   │   │   └── user.py            ← User model (template)
│   │   ├── schemas/
│   │   │   └── academic_schema.py ← Request/response models
│   │   ├── services/ai/
│   │   │   └── gemini.py          ← AI service client (template)
│   │   ├── authz.map.json         ← Role-based access control rules
│   │   └── main.py                ← FastAPI app bootstrap
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── app/(dashboard)/
│       │   └── academic/
│       │       ├── page.tsx        ← Student dashboard + login
│       │       └── advisor/
│       │           └── page.tsx    ← Agentic chat + resume upload + history
│       └── components/layout/
│           └── Sidebar.tsx         ← Navigation
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 📝 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Free API key from console.groq.com |
| `SECRET_KEY` | ✅ Yes | JWT signing key |
| `NEXTAUTH_SECRET` | ✅ Yes | NextAuth session secret |
| `DATABASE_URL` | Auto | Set by docker-compose |
| `GROQ_MODEL` | Optional | Default: `llama-3.1-8b-instant` |
| `GEMINI_API_KEY` | Optional | For template AI features (policies, insights) |

---

## 🎓 Demo Data

The seed creates:

**3 Departments:**
- CSE — Computer Science and Engineering
- BBA — Bachelor of Business Administration
- ISDI — Institute of Design

**12 Courses:**

| Department | Courses |
|---|---|
| CSE | Advanced Algorithms, Statistics for Computing, Mobile & Cloud Systems, Cybersecurity Fundamentals |
| BBA | Financial Accounting, Marketing Management, Organisational Behaviour, Business Strategy & Analytics |
| ISDI | Typography & Visual Communication, Motion Graphics & Animation, UX Design & Research, Design Thinking & Innovation |

**60 Students** with realistic CGPAs, random semesters (2–8), varied backlogs, and course enrollment history.

---

## ⚠️ Troubleshooting

| Problem | Fix |
|---|---|
| Backend container not starting | Run `docker compose logs backend` to see the error |
| Seeding failed | Backend may have crashed — check logs |
| AI not responding | Check `GROQ_API_KEY` is set correctly in `.env` |
| 429 Too Many Requests | Groq rate limit — wait 30 seconds and retry |
| Port already in use | Run `docker stop $(docker ps -aq)` then `docker compose up --build` |
| Student login failing | Make sure you seeded the database first |
| Resume search not working | Run `ALTER TABLE resume_chunks ADD COLUMN IF NOT EXISTS tfidf_vector TEXT;` in psql |
| Chat history not loading | Add `/api/academic/chat-history/{student_id}` to `authz.map.json` |
| Frontend not updating | Run `docker compose down` then `docker compose up --build` |

---

## 🏗️ Built On

This project is built on the **Atlas AI Command Centre** template which provides:
- FastAPI backend with async SQLAlchemy
- Next.js frontend with TypeScript
- PostgreSQL with automatic table creation
- JSON-based RBAC authorization engine
- Automatic audit logging middleware
- Docker Compose with 5 containers
- AI Manager global chatbot
- AI Policies and Insights pages