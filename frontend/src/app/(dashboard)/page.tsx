import DashboardOverview from "@/components/charts/DashboardOverview";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Command Center Overview</h1>
          <p className="text-slate-600 mt-0.5">
            Real-time status of Atlas University&apos;s agentic ecosystem.
          </p>
        </div>
        <button
          type="button"
          className="px-4 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
        >
          + New Agent
        </button>
      </div>

      <DashboardOverview />
    </div>
  );
}
