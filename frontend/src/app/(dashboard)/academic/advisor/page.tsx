'use client';
import { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { fetchWithAuth } from '@/lib/api';

function renderMarkdown(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^### (.*$)/gm, '<h3 style="font-weight:600;margin:8px 0 4px">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 style="font-weight:600;margin:8px 0 4px">$1</h2>')
    .replace(/^\d+\. (.*$)/gm, '<div style="display:flex;gap:8px;margin:4px 0"><span style="min-width:16px">•</span><span>$1</span></div>')
    .replace(/^- (.*$)/gm, '<div style="display:flex;gap:8px;margin:4px 0"><span style="min-width:16px">•</span><span>$1</span></div>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');
}

export default function AdvisorPage() {
  const searchParams = useSearchParams();
  const studentId = searchParams.get('student');
  const [profile, setProfile] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [resumeUploaded, setResumeUploaded] = useState(false);
  const [resumeName, setResumeName] = useState('');
  const [resumeUploading, setResumeUploading] = useState(false);
  const [hasHistory, setHasHistory] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const suggestions = [
    "What courses should I take next semester?",
    "Am I on track to graduate on time?",
    "What career path suits my profile?",
    "How can I improve my CGPA?",
    "Analyse my resume and find skill gaps",
    "What skills am I missing for my career goal?",
  ];

  useEffect(() => {
    const saved = sessionStorage.getItem('student_profile');
    const savedProfile = saved ? JSON.parse(saved) : null;
    const sid = studentId || savedProfile?.id;

    if (!sid) {
      setHistoryLoading(false);
      return;
    }

    Promise.all([
      fetchWithAuth(`/api/academic/profile/${sid}`).then(r => r.json()),
      fetchWithAuth(`/api/academic/chat-history/${sid}`).then(r => r.json()),
    ]).then(([profileData, historyData]) => {
      setProfile(profileData);
      if (Array.isArray(historyData) && historyData.length > 0) {
        setHasHistory(true);
        setMessages(historyData.map((m: any) => ({
          role: m.role,
          content: m.content,
          fromHistory: true,
        })));
      }
    }).catch(() => {
      const saved2 = sessionStorage.getItem('student_profile');
      const s2 = saved2 ? JSON.parse(saved2) : null;
      if (s2) setProfile(s2);
    }).finally(() => setHistoryLoading(false));
  }, [studentId]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  async function handleResumeUpload(file: File) {
    if (!file || file.type !== 'application/pdf') {
      alert('Please upload a PDF file');
      return;
    }
    const saved = sessionStorage.getItem('student_profile');
    const sid = studentId || (saved ? JSON.parse(saved)?.id : null);
    if (!sid) { alert('No student selected'); return; }

    setResumeUploading(true);
    try {
      const base64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve((reader.result as string).split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      await fetchWithAuth(`/api/academic/upload-resume/${sid}`, {
        method: 'POST',
        body: JSON.stringify({ pdf_base64: base64 }),
      });

      setResumeUploaded(true);
      setResumeName(file.name);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `I've stored and indexed your resume "${file.name}" using TF-IDF semantic search. I can now search through it to answer questions about your skills, experience, and career readiness. Try asking me to compare your resume with your career goal or identify skill gaps.`
      }]);
    } catch (e) {
      alert('Failed to upload resume. Please try again.');
    } finally {
      setResumeUploading(false);
    }
  }

  async function sendMessage(text: string) {
    const msg = text || input;
    if (!msg.trim()) return;
    const saved = sessionStorage.getItem('student_profile');
    const sid = studentId || (saved ? JSON.parse(saved)?.id : null);
    if (!sid) return;

    const newMessages = [...messages, { role: 'user', content: msg }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      // Include last 6 history messages for continuity
      const historyContext = messages
        .filter(m => m.fromHistory)
        .slice(-6)
        .map(m => ({ role: m.role, content: m.content }));

      const currentMessages = newMessages
        .filter(m => !m.fromHistory)
        .map(m => ({ role: m.role, content: m.content }));

      // Send history + current conversation so AI remembers previous discussions
      const messagesToSend = [...historyContext, ...currentMessages];

      const res = await fetchWithAuth('/api/academic/chat', {
        method: 'POST',
        body: JSON.stringify({
          messages: messagesToSend,
          student_id: parseInt(String(sid)),
        }),
      });
      const data = await res.json();
      setMessages([...newMessages, { role: 'assistant', content: data.content }]);
    } catch (e) {
      setMessages([...newMessages, {
        role: 'assistant',
        content: "I'm having trouble connecting right now. Please try again."
      }]);
    } finally {
      setLoading(false);
    }
  }

  const saved = typeof window !== 'undefined' ? sessionStorage.getItem('student_profile') : null;
  const sid = studentId || (saved ? JSON.parse(saved)?.id : null);
  const newMessages = messages.filter(m => !m.fromHistory);

  if (historyLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-80px)]">
        <div className="text-center space-y-3">
          <div className="inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-500 text-sm">Loading your conversation history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] max-w-4xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden m-4">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center gap-3">
        <div className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center text-white text-xl">🎓</div>
        <div className="flex-1">
          <h2 className="font-bold text-slate-800">AI Academic Advisor</h2>
          <p className="text-xs text-slate-500">
            {profile ? `Advising: ${profile.full_name} • CGPA ${profile.cgpa} • ${profile.department_name}` : 'Loading...'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {resumeUploaded && (
            <span className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full">📄 Resume indexed</span>
          )}
          {hasHistory && (
            <span className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full">🧠 Memory loaded</span>
          )}
          {profile?.is_at_risk && (
            <span className="text-xs font-bold bg-red-100 text-red-700 px-3 py-1 rounded-full">⚠️ At Risk</span>
          )}
        </div>
      </div>

      {/* Agent notice */}
      <div className="px-4 py-2 bg-indigo-50 border-b border-indigo-100 flex items-center justify-between">
        <p className="text-xs text-indigo-600 font-medium">
          🤖 Agentic mode — uses tools to fetch live data • TF-IDF resume search • persistent memory
        </p>
        {hasHistory && (
          <button
            onClick={() => { setMessages([]); setHasHistory(false); }}
            className="text-xs text-indigo-400 hover:text-indigo-600 underline"
          >
            Clear history
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/30">

        {/* History section */}
        {hasHistory && messages.some(m => m.fromHistory) && (
          <>
            <div className="flex items-center gap-3 py-1">
              <div className="flex-1 h-px bg-slate-200"></div>
              <span className="text-xs text-slate-400 whitespace-nowrap">— Previous conversations —</span>
              <div className="flex-1 h-px bg-slate-200"></div>
            </div>
            {messages.filter(m => m.fromHistory).map((m, i) => (
              <div key={`history-${i}`} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {m.role === 'assistant' && (
                  <div className="w-7 h-7 bg-indigo-100 rounded-full flex items-center justify-center text-sm mr-2 mt-1 shrink-0 opacity-60">🤖</div>
                )}
                <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed opacity-70 ${
                  m.role === 'user'
                    ? 'bg-indigo-400 text-white rounded-tr-none'
                    : 'bg-white text-slate-600 border border-slate-100 rounded-tl-none'
                }`}>
                  {m.role === 'user' ? (
                    <p className="whitespace-pre-wrap">{m.content}</p>
                  ) : (
                    <div dangerouslySetInnerHTML={{ __html: renderMarkdown(m.content) }} />
                  )}
                </div>
              </div>
            ))}
            <div className="flex items-center gap-3 py-1">
              <div className="flex-1 h-px bg-indigo-200"></div>
              <span className="text-xs text-indigo-400 whitespace-nowrap">— New conversation —</span>
              <div className="flex-1 h-px bg-indigo-200"></div>
            </div>
          </>
        )}

        {/* Empty state */}
        {newMessages.length === 0 && (
          <div className="text-center py-8 space-y-6">
            <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center text-3xl mx-auto">👋</div>
            <div>
              <h3 className="text-lg font-bold text-slate-700">
                {hasHistory ? 'Continue where you left off' : 'How can I help you today?'}
              </h3>
              <p className="text-slate-400 text-sm mt-1">
                {hasHistory ? 'The advisor remembers your previous conversations' : "I'll look up your live academic data before answering"}
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-xl mx-auto">
              {suggestions.map((s) => (
                <button key={s} onClick={() => sendMessage(s)}
                  className="p-3 text-left border border-slate-200 rounded-xl hover:bg-white hover:border-indigo-300 transition-all text-sm text-slate-600">
                  {s}
                </button>
              ))}
            </div>
            <div className="mt-2">
              <p className="text-slate-400 text-xs mb-2">Upload your resume for AI gap analysis</p>
              <button onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 border-2 border-dashed border-slate-300 rounded-xl text-slate-500 hover:border-indigo-400 hover:text-indigo-600 transition-all text-sm">
                📄 Upload Resume PDF
              </button>
            </div>
          </div>
        )}

        {/* New messages */}
        {newMessages.map((m, i) => (
          <div key={`new-${i}`} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'assistant' && (
              <div className="w-7 h-7 bg-indigo-100 rounded-full flex items-center justify-center text-sm mr-2 mt-1 shrink-0">🤖</div>
            )}
            <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              m.role === 'user'
                ? 'bg-indigo-600 text-white rounded-tr-none'
                : 'bg-white text-slate-700 border border-slate-200 rounded-tl-none shadow-sm'
            }`}>
              {m.role === 'user' ? (
                <p className="whitespace-pre-wrap">{m.content}</p>
              ) : (
                <div dangerouslySetInnerHTML={{ __html: renderMarkdown(m.content) }} />
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start items-center gap-2">
            <div className="w-7 h-7 bg-indigo-100 rounded-full flex items-center justify-center text-sm shrink-0">🤖</div>
            <div className="bg-white border border-slate-200 px-4 py-3 rounded-2xl rounded-tl-none shadow-sm">
              <div className="flex gap-1 items-center">
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.15s]"></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.3s]"></div>
                <span className="text-xs text-slate-400 ml-2">Calling tools...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-200 bg-white">
        {!sid && <p className="text-center text-sm text-slate-400 mb-2">Go back and select or log in as a student first.</p>}
        <div className="flex gap-2">
          <input ref={fileInputRef} type="file" accept=".pdf" className="hidden"
            onChange={(e) => { if (e.target.files?.[0]) handleResumeUpload(e.target.files[0]); e.target.value = ''; }} />
          <button onClick={() => fileInputRef.current?.click()} disabled={resumeUploading || !sid}
            title="Upload Resume PDF"
            className="p-2.5 border border-slate-300 rounded-xl text-slate-500 hover:border-indigo-400 hover:text-indigo-600 transition-colors disabled:opacity-50">
            {resumeUploading ? (
              <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            )}
          </button>
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage('')}
            placeholder={sid ? "Ask anything — the agent will look up your data..." : "Select a student first"}
            disabled={!sid || loading}
            className="flex-1 px-4 py-2.5 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 disabled:bg-slate-50" />
          <button onClick={() => sendMessage('')} disabled={!sid || !input.trim() || loading}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 text-white px-5 py-2.5 rounded-xl font-medium transition-colors text-sm">
            Send
          </button>
        </div>
        {resumeName && <p className="text-xs text-green-600 mt-2 ml-1">📄 {resumeName} indexed — ask me to analyse it</p>}
      </div>
    </div>
  );
}