"use client";

import { useEffect, useState } from "react";
import { fetchWithAuth } from "@/lib/api";

interface Insight {
  title: string;
  description: string;
  severity: "CRITICAL" | "WARNING" | "RECOMMENDATION";
  category: string;
  suggested_action: string;
  impact: string;
}

export default function AIInsightsPage() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => { loadInsights(); }, []);

  const loadInsights = async () => {
    try {
      const response = await fetchWithAuth("/api/ai/insights");
      if (!response.ok) throw new Error("Failed to load insights");
      const data = await response.json();
      setInsights(data);
    } catch (error) {
      console.error("Failed to load insights:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const response = await fetchWithAuth("/api/ai/insights/generate", { method: "POST" });
      if (!response.ok) throw new Error("Failed to generate insights");
      await loadInsights();
    } catch (error) {
      alert("Failed to generate insights");
      console.error(error);
    } finally {
      setGenerating(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return "bg-red-100 text-red-800 border-red-200";
      case "WARNING": return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "RECOMMENDATION": return "bg-blue-100 text-blue-800 border-blue-200";
      default: return "bg-slate-100 text-slate-800 border-slate-200";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return "🚨";
      case "WARNING": return "⚠️";
      case "RECOMMENDATION": return "💡";
      default: return "ℹ️";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-600">Loading insights...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">AI Insights</h1>
          <p className="text-slate-600 mt-1">Proactive analysis and recommendations</p>
        </div>
        <button onClick={handleGenerate} disabled={generating}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed">
          {generating ? "Generating..." : "🔄 Regenerate Insights"}
        </button>
      </div>

      <div className="grid gap-4">
        {insights.map((insight, index) => (
          <div key={index} className={`bg-white rounded-xl border-2 p-6 ${getSeverityColor(insight.severity)}`}>
            <div className="flex items-start gap-4">
              <span className="text-3xl">{getSeverityIcon(insight.severity)}</span>
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-slate-900">{insight.title}</h3>
                  <span className="px-2 py-1 text-xs font-medium rounded bg-white/50">{insight.category}</span>
                </div>
                <p className="text-slate-700 mb-4">{insight.description}</p>
                <div className="bg-white/70 rounded-lg p-4 mb-3">
                  <p className="text-xs font-medium text-slate-600 uppercase mb-1">Suggested Action</p>
                  <p className="text-slate-900">{insight.suggested_action}</p>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-sm font-medium text-slate-600">Expected Impact:</span>
                  <p className="text-sm text-slate-700">{insight.impact}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
        {insights.length === 0 && (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <p className="text-slate-600">No insights available. Click &quot;Regenerate Insights&quot; to analyze system data.</p>
          </div>
        )}
      </div>
    </div>
  );
}
