'use client';
import { useEffect, useState } from 'react';
import { fetchWithAuth } from '@/lib/api';
import Link from 'next/link';

function ProfileView({ profile, recs, career }: { profile: any; recs: any[]; career: any }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        {profile.backlogs > 0 && (
          <div className={`p-4 rounded-lg flex items-start gap-3 border-l-4 ${
            profile.backlogs >= 3 ? 'bg-red-50 border-red-500 text-red-800' : 'bg-amber-50 border-amber-500 text-amber-800'
          }`}>
            <span className="text-xl">⚠️</span>
            <div>
              <p className="font-bold">Academic Warning</p>
              <p className="text-sm">{profile.full_name} has {profile.backlogs} active backlog{profile.backlogs > 1 ? 's' : ''}.</p>
            </div>
          </div>
        )}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-800">{profile.full_name}</h2>
              <p className="text-slate-500">{profile.roll_number} • {profile.department_name}</p>
            </div>
            <span className={`px-4 py-2 rounded-full font-bold text-white text-sm ${
              profile.cgpa >= 8 ? 'bg-emerald-500' : profile.cgpa >= 6 ? 'bg-amber-500' : 'bg-red-500'
            }`}>CGPA {profile.cgpa}</span>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-3 bg-slate-50 rounded-lg">
              <p className="text-xs text-slate-400 uppercase font-bold mb-1">Semester</p>
              <p className="font-semibold text-slate-700">{profile.current_semester}</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <p className="text-xs text-slate-400 uppercase font-bold mb-1">Career Goal</p>
              <p className="font-semibold text-slate-700 capitalize">{profile.career_goal || 'Not set'}</p>
            </div>
          </div>
          <h3 className="font-bold text-slate-700 mb-3">Enrolled Courses</h3>
          <div className="space-y-2">
            {profile.enrollments.map((e: any) => (
              <div key={e.id} className="flex justify-between items-center p-3 border border-slate-100 rounded-lg">
                <div>
                  <p className="font-medium text-slate-700">{e.course.name}</p>
                  <p className="text-xs text-slate-400">{e.course.code} • {e.course.credits} credits</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                  e.status === 'completed' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                }`}>{e.status === 'completed' ? `Grade: ${e.grade}` : 'Ongoing'}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2"><span>🤖</span> AI Course Recommendations</h3>
          {recs.length === 0 ? (
            <p className="text-slate-400 text-sm">No recommendations available for next semester</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recs.map((rec: any, i: number) => (
                <div key={i} className="p-4 border border-slate-200 rounded-xl hover:border-indigo-300 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <p className="font-bold text-slate-800">{rec.name}</p>
                    <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">{rec.code}</span>
                  </div>
                  <p className="text-sm text-slate-600 mb-2">{rec.reason}</p>
                  <span className="text-xs bg-indigo-50 text-indigo-600 px-2 py-1 rounded-full">{rec.career_relevance}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      <div className="space-y-6">
        {career && career.path_title && (
          <div className="bg-gradient-to-br from-indigo-600 to-blue-700 p-6 rounded-2xl text-white shadow-lg">
            <p className="text-indigo-200 text-xs font-bold uppercase tracking-widest mb-1">Career Path</p>
            <h3 className="text-xl font-bold mb-4">{career.path_title}</h3>
            {career.skill_gaps?.length > 0 && (
              <div className="mb-4">
                <p className="text-indigo-200 text-xs font-bold uppercase mb-2">Skill Gaps</p>
                <div className="flex flex-wrap gap-2">
                  {career.skill_gaps.map((g: string, i: number) => (
                    <span key={i} className="bg-white/20 px-2 py-1 rounded text-xs">{g}</span>
                  ))}
                </div>
              </div>
            )}
            {career.action_steps?.length > 0 && (
              <div className="mb-4">
                <p className="text-indigo-200 text-xs font-bold uppercase mb-2">Action Steps</p>
                <ol className="space-y-2">
                  {career.action_steps.map((s: string, i: number) => (
                    <li key={i} className="flex gap-2 text-sm">
                      <span className="bg-white/20 w-5 h-5 rounded-full flex items-center justify-center text-xs shrink-0">{i + 1}</span>
                      <span className="text-indigo-100">{s}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}
            {career.outlook && (
              <div className="pt-4 border-t border-white/20">
                <p className="text-indigo-200 text-xs font-bold uppercase mb-1">Outlook</p>
                <p className="text-sm text-white">{career.outlook}</p>
              </div>
            )}
          </div>
        )}
        <Link href={`/academic/advisor?student=${profile.id}`}
          className="flex items-center justify-center gap-2 w-full py-4 bg-white border-2 border-slate-200 hover:border-indigo-500 hover:text-indigo-600 text-slate-700 font-bold rounded-xl transition-all shadow-sm">
          <span>💬</span> Chat with AI Advisor
        </Link>
      </div>
    </div>
  );
}

export default function AcademicPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [profile, setProfile] = useState<any>(null);
  const [recs, setRecs] = useState<any[]>([]);
  const [career, setCareer] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState('');
  const [loggedInStudent, setLoggedInStudent] = useState<any>(null);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState('');

  useEffect(() => {
    const saved = sessionStorage.getItem('student_profile');
    if (saved) {
      const p = JSON.parse(saved);
      setLoggedInStudent(p);
      setProfile(p);
      loadExtras(p.id);
    } else {
      loadStudents();
    }
  }, []);

  async function loadStudents() {
    try {
      const res = await fetchWithAuth('/api/academic/students');
      const data = await res.json();
      setStudents(Array.isArray(data) ? data : []);
    } catch (e) { setError('Failed to load students'); }
  }

  async function loadExtras(id: number) {
    try {
      const [rRes, cRes] = await Promise.all([
        fetchWithAuth(`/api/academic/recommendations/${id}`),
        fetchWithAuth(`/api/academic/career-path/${id}`),
      ]);
      const [r, c] = await Promise.all([rRes.json(), cRes.json()]);
      setRecs(Array.isArray(r) ? r : []);
      setCareer(c);
    } catch (e) {}
  }

  async function handleStudentLogin() {
    if (!loginEmail.trim() || !loginPassword.trim()) {
      setLoginError('Please enter both email and password.');
      return;
    }
    setLoginLoading(true);
    setLoginError('');
    try {
      const res = await fetchWithAuth('/api/academic/student-login', {
        method: 'POST',
        body: JSON.stringify({
          email: loginEmail.trim().toLowerCase(),
          password: loginPassword,
        }),
      });
      if (!res.ok) {
        setLoginError('Invalid email or password. Try au2022cse001@atlasuniversity.edu.in / student123');
        return;
      }
      const data = await res.json();
      sessionStorage.setItem('student_profile', JSON.stringify(data));
      setLoggedInStudent(data);
      setProfile(data);
      loadExtras(data.id);
    } catch (e) {
      setLoginError('Login failed. Please try again.');
    } finally {
      setLoginLoading(false);
    }
  }

  function handleLogout() {
    sessionStorage.removeItem('student_profile');
    setLoggedInStudent(null);
    setProfile(null);
    setRecs([]); setCareer(null);
    setLoginEmail(''); setLoginPassword('');
    loadStudents();
  }

  async function handleSeed() {
    setSeeding(true);
    setError('');
    try {
      const res = await fetchWithAuth('/api/academic/seed', { method: 'POST' });
      const data = await res.json();
      await loadStudents();
    } catch (e) { setError('Seeding failed'); }
    finally { setSeeding(false); }
  }

  async function loadStudent(id: string) {
    if (!id) { setProfile(null); return; }
    setSelectedId(id); setLoading(true); setError('');
    try {
      const pRes = await fetchWithAuth(`/api/academic/profile/${id}`);
      const p = await pRes.json();
      setProfile(p);
      loadExtras(parseInt(id));
    } catch (e) { setError('Failed to load student data'); }
    finally { setLoading(false); }
  }

  if (loggedInStudent) {
    return (
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <div>
            <h1 className="text-xl font-bold text-slate-800">My Academic Profile</h1>
            <p className="text-slate-500 text-sm">Welcome back, {loggedInStudent.full_name}</p>
          </div>
          <button onClick={handleLogout} className="px-4 py-2 border border-slate-300 text-slate-600 rounded-lg text-sm hover:bg-slate-50">Sign Out</button>
        </div>
        {!profile ? (
          <div className="text-center py-20"><div className="inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div></div>
        ) : <ProfileView profile={profile} recs={recs} career={career} />}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-wrap justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-200 gap-4">
        <h1 className="text-xl font-bold text-slate-800">Academic Advisor</h1>
        <div className="flex gap-3 items-center">
          <button onClick={handleSeed} disabled={seeding} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50">
            {seeding ? 'Seeding...' : 'Seed Database'}
          </button>
          <select className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" value={selectedId} onChange={(e) => loadStudent(e.target.value)}>
            <option value="">Select a Student (Admin)</option>
            {students.map((s) => <option key={s.id} value={s.id}>{s.name} ({s.roll})</option>)}
          </select>
        </div>
      </div>

      {error && <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
          <h2 className="text-xl font-bold text-slate-800 mb-1">Student Login</h2>
          <p className="text-slate-500 text-sm mb-6">Log in to view your own academic profile</p>
          <div className="space-y-3">
            <input
              type="email"
              value={loginEmail}
              onChange={(e) => setLoginEmail(e.target.value)}
              placeholder="au2022cse001@atlasuniversity.edu.in"
              className="w-full px-4 py-2.5 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            />
            <input
              type="password"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleStudentLogin()}
              placeholder="Password (student123)"
              className="w-full px-4 py-2.5 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            />
            {loginError && <p className="text-red-600 text-sm">{loginError}</p>}
            <button
              onClick={handleStudentLogin}
              disabled={loginLoading || !loginEmail.trim() || !loginPassword.trim()}
              className="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {loginLoading ? 'Logging in...' : 'View My Profile'}
            </button>
            <p className="text-xs text-slate-400 text-center">Format: rollnumber@atlasuniversity.edu.in</p>
          </div>
        </div>
        <div className="bg-gradient-to-br from-indigo-600 to-blue-700 p-8 rounded-2xl text-white">
          <h3 className="text-xl font-bold mb-3">Your AI Academic Advisor</h3>
          <p className="text-indigo-100 text-sm leading-relaxed mb-4">Get personalised course recommendations, career path projections, and instant AI advice based on your actual grades.</p>
          <ul className="space-y-2 text-sm text-indigo-100">
            <li className="flex items-center gap-2"><span>✓</span> Agentic AI that looks up your live data</li>
            <li className="flex items-center gap-2"><span>✓</span> Personalised course recommendations</li>
            <li className="flex items-center gap-2"><span>✓</span> Career path projection</li>
            <li className="flex items-center gap-2"><span>✓</span> Resume analysis with RAG</li>
          </ul>
        </div>
      </div>

      {students.length === 0 && !loading && (
        <div className="text-center py-20 bg-white rounded-xl border border-slate-200">
          <p className="text-slate-500 text-lg mb-2">No students in database</p>
          <p className="text-slate-400 text-sm">Click "Seed Database" to populate with 60 students</p>
        </div>
      )}

      {loading && <div className="text-center py-20"><div className="inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div></div>}
      {!loading && profile && <ProfileView profile={profile} recs={recs} career={career} />}
    </div>
  );
}