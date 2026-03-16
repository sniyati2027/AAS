"use client";

import { useEffect, useState } from "react";
import { fetchWithAuth } from "@/lib/api";

interface Policy {
  id: number;
  name: string;
  description: string | null;
  policy_type: string;
  natural_language: string | null;
  dsl: string | null;
  status: string;
  priority: number;
  created_at: string;
}

export default function AIPoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newPolicy, setNewPolicy] = useState({ name: "", description: "", natural_language: "" });
  const [translating, setTranslating] = useState(false);
  const [translatedDSL, setTranslatedDSL] = useState("");

  useEffect(() => { loadPolicies(); }, []);

  const loadPolicies = async () => {
    try {
      const response = await fetchWithAuth("/api/ai/policies");
      if (!response.ok) throw new Error("Failed to load policies");
      const data = await response.json();
      setPolicies(data);
    } catch (error) {
      console.error("Failed to load policies:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleTranslate = async () => {
    if (!newPolicy.natural_language.trim()) return;
    setTranslating(true);
    try {
      const response = await fetchWithAuth("/api/ai/policies/translate", {
        method: "POST",
        body: JSON.stringify({ natural_language: newPolicy.natural_language }),
      });
      if (!response.ok) throw new Error("Failed to translate policy");
      const data = await response.json();
      setTranslatedDSL(data.dsl);
    } catch (error) {
      alert("Failed to translate policy");
      console.error(error);
    } finally {
      setTranslating(false);
    }
  };

  const handleCreate = async () => {
    if (!newPolicy.name.trim() || !translatedDSL) return;
    try {
      const response = await fetchWithAuth("/api/ai/policies", {
        method: "POST",
        body: JSON.stringify({
          name: newPolicy.name,
          description: newPolicy.description,
          policy_type: "NATURAL_LANGUAGE",
          natural_language: newPolicy.natural_language,
          dsl: translatedDSL,
          priority: 100,
        }),
      });
      if (!response.ok) throw new Error("Failed to create policy");
      setShowCreateModal(false);
      setNewPolicy({ name: "", description: "", natural_language: "" });
      setTranslatedDSL("");
      await loadPolicies();
    } catch (error) {
      alert("Failed to create policy");
      console.error(error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-600">Loading policies...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">AI Policies</h1>
          <p className="text-slate-600 mt-1">Natural language access control rules</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
          + Create Policy
        </button>
      </div>

      <div className="grid gap-4">
        {policies.map((policy) => (
          <div key={policy.id} className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-slate-900">{policy.name}</h3>
                {policy.description && <p className="text-slate-600 text-sm mt-1">{policy.description}</p>}
                {policy.natural_language && (
                  <div className="mt-4">
                    <p className="text-xs font-medium text-slate-500 uppercase mb-1">Natural Language</p>
                    <p className="text-slate-700 italic">{policy.natural_language}</p>
                  </div>
                )}
                {policy.dsl && (
                  <div className="mt-4">
                    <p className="text-xs font-medium text-slate-500 uppercase mb-1">Translated DSL</p>
                    <pre className="text-sm bg-slate-50 p-3 rounded border border-slate-200 overflow-x-auto">{policy.dsl}</pre>
                  </div>
                )}
              </div>
              <div className="flex flex-col items-end gap-2 ml-4">
                <span className={`px-2 py-1 text-xs font-medium rounded ${policy.status === "ACTIVE" ? "bg-green-100 text-green-800" : "bg-slate-100 text-slate-800"}`}>
                  {policy.status}
                </span>
                <span className="text-xs text-slate-500">Priority: {policy.priority}</span>
              </div>
            </div>
          </div>
        ))}
        {policies.length === 0 && (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <p className="text-slate-600">No policies found. Create your first policy!</p>
          </div>
        )}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Create New Policy</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Policy Name *</label>
                <input type="text" value={newPolicy.name} onChange={(e) => setNewPolicy({ ...newPolicy, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Finance Report Access" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                <input type="text" value={newPolicy.description} onChange={(e) => setNewPolicy({ ...newPolicy, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Optional description" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Natural Language Rule *</label>
                <textarea value={newPolicy.natural_language} onChange={(e) => setNewPolicy({ ...newPolicy, natural_language: e.target.value })}
                  rows={4} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Allow managers to access financial reports during business hours" />
              </div>
              <button onClick={handleTranslate} disabled={translating || !newPolicy.natural_language.trim()}
                className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed">
                {translating ? "Translating..." : "Translate to DSL"}
              </button>
              {translatedDSL && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Translated DSL</label>
                  <pre className="text-sm bg-slate-50 p-3 rounded border border-slate-200 overflow-x-auto">{translatedDSL}</pre>
                </div>
              )}
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => { setShowCreateModal(false); setNewPolicy({ name: "", description: "", natural_language: "" }); setTranslatedDSL(""); }}
                className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors font-medium">
                Cancel
              </button>
              <button onClick={handleCreate} disabled={!newPolicy.name.trim() || !translatedDSL}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed">
                Create Policy
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
