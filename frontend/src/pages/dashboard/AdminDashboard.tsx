import { useEffect, useState } from 'react';
import client from '../../api/client';
import type { AdminDashboard as AdminDashboardType } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function AdminDashboard() {
  const [data, setData] = useState<AdminDashboardType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get('/dashboard/admin').then((r) => {
      setData(r.data);
      setLoading(false);
    });
  }, []);

  if (loading || !data) return <LoadingSpinner />;

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-100">Admin Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">System-wide overview and agent performance</p>
      </div>

      {/* Complaint stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-8 stagger-children">
        <MiniStat label="Total" value={data.total_complaints} color="text-gray-200" />
        <MiniStat label="Submitted" value={data.submitted} color="text-amber-400" />
        <MiniStat label="Assigned" value={data.assigned} color="text-blue-400" />
        <MiniStat label="In Progress" value={data.in_progress} color="text-purple-400" />
        <MiniStat label="Resolved" value={data.resolved} color="text-emerald-400" />
        <MiniStat label="Closed" value={data.closed} color="text-gray-400" />
        <MiniStat label="Unassigned" value={data.unassigned} color="text-red-400" />
      </div>

      {/* Agent overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        <div className="stat-card">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent pointer-events-none" />
          <p className="relative text-sm text-gray-400">Total Agents</p>
          <p className="relative text-3xl font-bold mt-1 text-purple-400">{data.total_agents}</p>
        </div>
        <div className="stat-card">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent pointer-events-none" />
          <p className="relative text-sm text-gray-400">Active Agents</p>
          <p className="relative text-3xl font-bold mt-1 text-emerald-400">{data.active_agents}</p>
        </div>
      </div>

      {/* Agent performance table */}
      <div className="glass-card overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-800/60">
          <h3 className="text-sm font-semibold text-gray-300">Agent Performance</h3>
        </div>
        {data.agent_performance.length === 0 ? (
          <div className="px-5 py-10 text-center text-gray-500 text-sm">
            No agents registered yet.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Agent</th>
                <th>Assigned</th>
                <th>Resolved</th>
                <th>Open</th>
                <th>Resolution Rate</th>
                <th>Avg Time (hrs)</th>
              </tr>
            </thead>
            <tbody>
              {data.agent_performance.map((ap) => (
                <tr key={ap.agent.id}>
                  <td>
                    <div>
                      <p className="font-medium text-gray-200">{ap.agent.name}</p>
                      <p className="text-xs text-gray-500">{ap.agent.email}</p>
                    </div>
                  </td>
                  <td className="font-semibold">{ap.total_assigned}</td>
                  <td className="font-semibold text-emerald-400">{ap.total_resolved}</td>
                  <td className="font-semibold text-amber-400">{ap.total_open}</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden max-w-[80px]">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(ap.resolution_rate, 100)}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-300">{ap.resolution_rate}%</span>
                    </div>
                  </td>
                  <td className="text-gray-400">
                    {ap.avg_resolution_hours != null ? `${ap.avg_resolution_hours}h` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function MiniStat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="stat-card text-center">
      <p className="text-xs text-gray-500 font-medium">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
    </div>
  );
}
