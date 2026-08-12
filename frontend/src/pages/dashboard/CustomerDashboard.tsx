import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import client from '../../api/client';
import type { CustomerDashboard as CustomerDashboardType } from '../../types';
import StatusBadge from '../../components/StatusBadge';
import PriorityBadge from '../../components/PriorityBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function CustomerDashboard() {
  const [data, setData] = useState<CustomerDashboardType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get('/dashboard/customer').then((r) => {
      setData(r.data);
      setLoading(false);
    });
  }, []);

  if (loading || !data) return <LoadingSpinner />;

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-100">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Your complaint overview</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8 stagger-children">
        <StatCard label="Total Complaints" value={data.total_complaints} color="blue" />
        <StatCard label="Open" value={data.open_complaints} color="amber" />
        <StatCard label="Resolved" value={data.resolved_complaints} color="emerald" />
      </div>

      {/* Quick action */}
      <div className="mb-6">
        <Link to="/complaints/new" className="btn-primary inline-flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Submit New Complaint
        </Link>
      </div>

      {/* Recent complaints */}
      <div className="glass-card overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-800/60">
          <h3 className="text-sm font-semibold text-gray-300">Recent Complaints</h3>
        </div>
        {data.recent_complaints.length === 0 ? (
          <div className="px-5 py-10 text-center text-gray-500 text-sm">
            No complaints yet. Submit one to get started!
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Submitted</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_complaints.map((c) => (
                <tr key={c.id}>
                  <td>
                    <Link to={`/complaints/${c.id}`} className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
                      {c.title}
                    </Link>
                  </td>
                  <td><StatusBadge status={c.status} /></td>
                  <td><PriorityBadge priority={c.priority} /></td>
                  <td className="text-sm text-gray-500">{new Date(c.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

/* ── Stat card sub-component ─────────────────────────────────── */

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  const gradients: Record<string, string> = {
    blue: 'from-blue-500/10 to-transparent',
    amber: 'from-amber-500/10 to-transparent',
    emerald: 'from-emerald-500/10 to-transparent',
  };
  const textColors: Record<string, string> = {
    blue: 'text-blue-400',
    amber: 'text-amber-400',
    emerald: 'text-emerald-400',
  };

  return (
    <div className="stat-card">
      <div className={`absolute inset-0 bg-gradient-to-br ${gradients[color]} pointer-events-none`} />
      <p className="relative text-sm text-gray-400 font-medium">{label}</p>
      <p className={`relative text-3xl font-bold mt-1 ${textColors[color]}`}>{value}</p>
    </div>
  );
}
