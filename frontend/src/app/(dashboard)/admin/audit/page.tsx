"use client";

import { useEffect, useState } from "react";
import { fetchWithAuth } from "@/lib/api";

interface AuditLog {
  id: number;
  user_id: number | null;
  action: string;
  ip_address: string | null;
  details: string;
  timestamp: string;
}

export default function AdminAuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    loadLogs();
  }, [limit]);

  const loadLogs = async () => {
    try {
      const response = await fetchWithAuth(`/api/admin/audit?limit=${limit}`);
      if (!response.ok) throw new Error("Failed to load audit logs");
      const data = await response.json();
      setLogs(data.logs);
    } catch (error) {
      console.error("Failed to load audit logs:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await fetchWithAuth("/api/admin/audit/export");
      if (!response.ok) throw new Error("Failed to export logs");
      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert("Failed to export logs");
      console.error(error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-600">Loading audit logs...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Audit Logs</h1>
          <p className="text-slate-600 mt-1">System activity and security events</p>
        </div>
        <button onClick={handleExport} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
          Export Logs
        </button>
      </div>

      <div className="flex gap-4 items-center">
        <label className="text-sm font-medium text-slate-700">Show:</label>
        <select
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value={25}>25 logs</option>
          <option value={50}>50 logs</option>
          <option value={100}>100 logs</option>
          <option value={500}>500 logs</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-600 uppercase">Timestamp</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-600 uppercase">Action</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-600 uppercase">User ID</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-600 uppercase">IP Address</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-600 uppercase">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50">
                  <td className="px-6 py-4 text-sm text-slate-900 whitespace-nowrap">{new Date(log.timestamp).toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex px-2 py-1 text-xs font-mono rounded bg-slate-100 text-slate-800">{log.action}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">{log.user_id || "-"}</td>
                  <td className="px-6 py-4 text-sm text-slate-600 font-mono">{log.ip_address || "-"}</td>
                  <td className="px-6 py-4 text-sm text-slate-600 max-w-md truncate" title={log.details}>{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {logs.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-600">No audit logs found</p>
          </div>
        )}
      </div>
    </div>
  );
}
