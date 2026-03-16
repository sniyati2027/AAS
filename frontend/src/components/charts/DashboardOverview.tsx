"use client";

const overviewCards = [
  {
    title: "Active AI Agents",
    value: "24",
    tag: "+4 new",
    tagColor: "bg-blue-100 text-blue-700",
    icon: (
      <svg className="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    title: "Running Automations",
    value: "142",
    tag: "Stable",
    tagColor: "bg-violet-100 text-violet-700",
    icon: (
      <svg className="w-8 h-8 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
  },
  {
    title: "Total Projects",
    value: "8",
    tag: "2 Due",
    tagColor: "bg-amber-100 text-amber-700",
    icon: (
      <svg className="w-8 h-8 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    title: "System Health",
    value: "99.9%",
    tag: "Excellent",
    tagColor: "bg-emerald-100 text-emerald-700",
    icon: (
      <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
];

const liveActivity = [
  { agent: "Timetable AI", task: "Generating week 12 schedule", status: "PROCESSING", statusColor: "bg-blue-100 text-blue-700", priority: "High", priorityColor: "bg-red-500" },
  { agent: "HR Automation", task: "Leave request #402", status: "IDLE", statusColor: "bg-slate-100 text-slate-600", priority: "Medium", priorityColor: "bg-amber-500" },
  { agent: "Doc Intelligence", task: "Extracting from syllabus.pdf", status: "SUCCESS", statusColor: "bg-emerald-100 text-emerald-700", priority: "Low", priorityColor: "bg-slate-400" },
];

const systemActivity = [
  { event: "Automation Triggered", time: "2 min ago", dot: "bg-blue-500" },
  { event: "Knowledge Base Updated", time: "15 min ago", dot: "bg-violet-500" },
  { event: "Warning Alert", time: "1 hour ago", dot: "bg-amber-500" },
];

export default function DashboardOverview() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {overviewCards.map((card) => (
          <div
            key={card.title}
            className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">{card.title}</p>
                <p className="text-2xl font-bold text-slate-900 mt-1">{card.value}</p>
                <span className={`inline-block mt-2 px-2 py-0.5 rounded text-xs font-medium ${card.tagColor}`}>
                  {card.tag}
                </span>
              </div>
              <div className="p-2 bg-slate-50 rounded-lg">{card.icon}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
            <h2 className="font-semibold text-slate-900">Live Agent Activity</h2>
            <a href="#" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">View All</a>
          </div>
          <div className="divide-y divide-slate-100">
            {liveActivity.map((row, i) => (
              <div key={i} className="px-5 py-3 flex items-center gap-4 hover:bg-slate-50/50">
                <span className={`w-2 h-2 rounded-full shrink-0 ${row.priorityColor}`} />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-slate-900 truncate">{row.agent}</p>
                  <p className="text-sm text-slate-500 truncate">{row.task}</p>
                </div>
                <span className={`px-2 py-0.5 rounded text-xs font-medium shrink-0 ${row.statusColor}`}>
                  {row.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-200">
            <h2 className="font-semibold text-slate-900">System Activity</h2>
          </div>
          <div className="divide-y divide-slate-100">
            {systemActivity.map((row, i) => (
              <div key={i} className="px-5 py-3 flex items-center gap-3 hover:bg-slate-50/50">
                <span className={`w-2 h-2 rounded-full shrink-0 ${row.dot}`} />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-slate-900">{row.event}</p>
                  <p className="text-sm text-slate-500">{row.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
