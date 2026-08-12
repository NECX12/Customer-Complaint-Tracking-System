import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import client from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import type { ComplaintListResponse, ComplaintStatus } from '../../types';
import StatusBadge from '../../components/StatusBadge';
import PriorityBadge from '../../components/PriorityBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

const ALL_STATUSES: ComplaintStatus[] = ['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'];

export default function ComplaintList() {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState<ComplaintListResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    fetchComplaints();
  }, [statusFilter]);

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (statusFilter) params.status = statusFilter;
      const res = await client.get('/complaints', { params });
      setComplaints(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Complaints</h1>
          <p className="text-gray-500 text-sm mt-1">
            {user?.role === 'CUSTOMER' ? 'Your submitted complaints' :
             user?.role === 'AGENT' ? 'Your assigned complaints' : 'All complaints'}
          </p>
        </div>
        {user?.role === 'CUSTOMER' && (
          <Link to="/complaints/new" className="btn-primary inline-flex items-center gap-2 text-sm">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            New Complaint
          </Link>
        )}
      </div>

      {/* Status filter (admin only) */}
      {user?.role === 'ADMIN' && (
        <div className="flex gap-2 mb-6 flex-wrap">
          <button
            onClick={() => setStatusFilter('')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all duration-200 ${
              !statusFilter
                ? 'bg-blue-500/15 text-blue-400 border-blue-500/30'
                : 'bg-gray-800/40 text-gray-500 border-gray-700/40 hover:text-gray-300'
            }`}
          >
            All
          </button>
          {ALL_STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all duration-200 ${
                statusFilter === s
                  ? 'bg-blue-500/15 text-blue-400 border-blue-500/30'
                  : 'bg-gray-800/40 text-gray-500 border-gray-700/40 hover:text-gray-300'
              }`}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      )}

      {/* Table */}
      {loading ? (
        <LoadingSpinner />
      ) : complaints.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <div className="text-4xl mb-3">📋</div>
          <p className="text-gray-400 font-medium">No complaints found</p>
          <p className="text-gray-600 text-sm mt-1">
            {user?.role === 'CUSTOMER' ? 'Submit your first complaint to get started.' : 'Nothing to show for the current filter.'}
          </p>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Created</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {complaints.map((c) => (
                <tr key={c.id}>
                  <td>
                    <Link
                      to={`/complaints/${c.id}`}
                      className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                    >
                      {c.title}
                    </Link>
                  </td>
                  <td><StatusBadge status={c.status} /></td>
                  <td><PriorityBadge priority={c.priority} /></td>
                  <td className="text-sm text-gray-500 whitespace-nowrap">
                    {new Date(c.created_at).toLocaleDateString()}
                  </td>
                  <td className="text-sm text-gray-500 whitespace-nowrap">
                    {new Date(c.updated_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
