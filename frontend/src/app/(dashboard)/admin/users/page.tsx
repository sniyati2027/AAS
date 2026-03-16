"use client";

import { useEffect, useState } from "react";
import { fetchWithAuth } from "@/lib/api";

interface User {
  id: number;
  email: string;
  role: string;
  status: string;
  is_active: boolean;
  created_at: string;
  approved_at?: string;
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"all" | "pending">("all");

  useEffect(() => {
    loadUsers();
    loadPendingUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await fetchWithAuth("/api/admin/users");
      if (!response.ok) throw new Error("Failed to load users");
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error("Failed to load users:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadPendingUsers = async () => {
    try {
      const response = await fetchWithAuth("/api/admin/users/pending");
      if (!response.ok) throw new Error("Failed to load pending users");
      const data = await response.json();
      setPendingUsers(data);
    } catch (error) {
      console.error("Failed to load pending users:", error);
    }
  };

  const handleApprove = async (userId: number) => {
    if (!confirm("Approve this user?")) return;
    try {
      const response = await fetchWithAuth(`/api/admin/users/${userId}/approve`, { method: "POST" });
      if (!response.ok) throw new Error("Failed to approve user");
      await loadUsers();
      await loadPendingUsers();
    } catch (error) {
      alert("Failed to approve user");
      console.error(error);
    }
  };

  const handleReject = async (userId: number) => {
    if (!confirm("Reject this user? This action cannot be undone.")) return;
    try {
      const response = await fetchWithAuth(`/api/admin/users/${userId}/reject`, { method: "POST" });
      if (!response.ok) throw new Error("Failed to reject user");
      await loadUsers();
      await loadPendingUsers();
    } catch (error) {
      alert("Failed to reject user");
      console.error(error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-600">Loading users...</p>
      </div>
    );
  }

  const displayUsers = activeTab === "all" ? users : pendingUsers;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">User Management</h1>
        <p className="text-slate-600 mt-1">Manage user accounts and approvals</p>
      </div>

      <div className="flex gap-4 border-b border-slate-200">
        <button
          onClick={() => setActiveTab("all")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "all" ? "text-blue-600 border-b-2 border-blue-600" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          All Users ({users.length})
        </button>
        <button
          onClick={() => setActiveTab("pending")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "pending" ? "text-blue-600 border-b-2 border-blue-600" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          Pending Approval ({pendingUsers.length})
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-600 uppercase">Email</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-600 uppercase">Role</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-600 uppercase">Status</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-600 uppercase">Created</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-slate-600 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {displayUsers.map((user) => (
                <tr key={user.id} className="hover:bg-slate-50">
                  <td className="px-6 py-4 text-sm text-slate-900">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded ${
                      user.status === "APPROVED" ? "bg-green-100 text-green-800"
                      : user.status === "PENDING" ? "bg-yellow-100 text-yellow-800"
                      : "bg-red-100 text-red-800"
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    {user.status === "PENDING" && (
                      <>
                        <button onClick={() => handleApprove(user.id)} className="px-3 py-1 text-sm font-medium text-green-700 hover:text-green-800 hover:bg-green-50 rounded transition-colors">Approve</button>
                        <button onClick={() => handleReject(user.id)} className="px-3 py-1 text-sm font-medium text-red-700 hover:text-red-800 hover:bg-red-50 rounded transition-colors">Reject</button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {displayUsers.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-600">No users found</p>
          </div>
        )}
      </div>
    </div>
  );
}
