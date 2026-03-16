"use client";

import { useState } from "react";
import AIManager from "@/components/ai/AIManager";

export default function Header() {
  const [showAIManager, setShowAIManager] = useState(false);

  return (
    <>
      <header className="h-14 border-b border-slate-200 bg-white px-6 flex items-center gap-4 shrink-0">
        <div className="flex-1 flex items-center">
          <div className="relative w-full max-w-md">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </span>
            <input
              type="search"
              placeholder="Search..."
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg bg-slate-50 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            />
          </div>
        </div>

        <button
          type="button"
          onClick={() => setShowAIManager(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white transition-colors font-medium"
          title="Open AI Manager"
        >
          <span className="text-lg">🤖</span>
          <span className="hidden sm:inline">AI Manager</span>
        </button>

        <div className="flex items-center gap-2 text-sm text-slate-600">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            System: Optimal
          </span>
        </div>

        <button type="button" className="p-2 rounded-lg hover:bg-slate-100 text-slate-500" aria-label="Notifications">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </button>

        <div className="flex items-center gap-3 pl-2 border-l border-slate-200">
          <div className="w-9 h-9 rounded-full bg-[var(--sidebar-bg)] flex items-center justify-center text-white font-semibold text-sm">
            A
          </div>
        </div>
      </header>

      <AIManager isOpen={showAIManager} onClose={() => setShowAIManager(false)} />
    </>
  );
}
