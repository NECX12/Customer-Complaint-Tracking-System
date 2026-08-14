import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import client from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import type {
  ComplaintResponse,
  StatusHistoryResponse,
  UserResponse,
  ComplaintStatus,
  VALID_TRANSITIONS as VT,
} from '../../types';
import StatusBadge from '../../components/StatusBadge';
import PriorityBadge from '../../components/PriorityBadge';
import Timeline from '../../components/Timeline';
import LoadingSpinner from '../../components/LoadingSpinner';
import AiSuggestionPanel from '../../components/AiSuggestionPanel';

// Local copy of the state machine
const VALID_TRANSITIONS: Record<ComplaintStatus, ComplaintStatus[]> = {
  SUBMITTED: ['ASSIGNED'],
  ASSIGNED: ['IN_PROGRESS'],
  IN_PROGRESS: ['RESOLVED'],
  RESOLVED: ['CLOSED', 'IN_PROGRESS'],
  CLOSED: [],
};

export default function ComplaintDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [complaint, setComplaint] = useState<ComplaintResponse | null>(null);
  const [history, setHistory] = useState<StatusHistoryResponse[]>([]);
  const [agents, setAgents] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Status update form
  const [newStatus, setNewStatus] = useState('');
  const [statusComment, setStatusComment] = useState('');
  const [statusLoading, setStatusLoading] = useState(false);

  // Assignment form
  const [selectedAgent, setSelectedAgent] = useState('');
  const [assignComment, setAssignComment] = useState('');
  const [assignLoading, setAssignLoading] = useState(false);

  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [complaintRes, historyRes] = await Promise.all([
        client.get(`/complaints/${id}`),
        client.get(`/complaints/${id}/history`),
      ]);
      setComplaint(complaintRes.data);
      setHistory(historyRes.data);

      // Fetch agents for admin assignment
      if (user?.role === 'ADMIN') {
        try {
          const agentsRes = await client.get('/users/agents');
          setAgents(agentsRes.data);
        } catch {}
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Complaint not found');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async () => {
    if (!newStatus) return;
    setStatusLoading(true);
    setError('');
    try {
      const res = await client.put(`/complaints/${id}/status`, {
        status: newStatus,
        comment: statusComment || undefined,
      });
      setComplaint(res.data);
      setNewStatus('');
      setStatusComment('');
      setSuccessMsg('Status updated — customer has been notified.');
      setTimeout(() => setSuccessMsg(''), 4000);
      // Refresh history
      const histRes = await client.get(`/complaints/${id}/history`);
      setHistory(histRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update status');
    } finally {
      setStatusLoading(false);
    }
  };

  const handleAssign = async () => {
    if (!selectedAgent) return;
    setAssignLoading(true);
    setError('');
    try {
      const res = await client.post(`/complaints/${id}/assign`, {
        agent_id: selectedAgent,
        comment: assignComment || undefined,
      });
      setComplaint(res.data);
      setSelectedAgent('');
      setAssignComment('');
      setSuccessMsg('Agent assigned — they have been notified.');
      setTimeout(() => setSuccessMsg(''), 4000);
      // Refresh history
      const histRes = await client.get(`/complaints/${id}/history`);
      setHistory(histRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to assign agent');
    } finally {
      setAssignLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  if (error && !complaint) {
    return (
      <div className="animate-fade-in text-center py-20">
        <div className="text-4xl mb-3">🚫</div>
        <p className="text-gray-400 font-medium">{error}</p>
        <button onClick={() => navigate('/complaints')} className="btn-secondary mt-4 text-sm">
          Back to Complaints
        </button>
      </div>
    );
  }

  if (!complaint) return null;

  const allowedTransitions = VALID_TRANSITIONS[complaint.status] || [];
  // Agents can only change status (not ASSIGNED — that's done via assign endpoint)
  const agentTransitions = allowedTransitions.filter((s) => s !== 'ASSIGNED');
  const canUpdateStatus =
    (user?.role === 'AGENT' || user?.role === 'ADMIN') && agentTransitions.length > 0;
  const canAssign = user?.role === 'ADMIN';

  return (
    <div className="animate-fade-in">
      {/* Back button */}
      <button
        onClick={() => navigate('/complaints')}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-300 transition-colors mb-6"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Complaints
      </button>

      {/* Success message */}
      {successMsg && (
        <div className="mb-4 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm animate-fade-in">
          ✓ {successMsg}
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="mb-4 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── Left column: complaint info ───────────────────── */}
        <div className="lg:col-span-2 space-y-6">
          {/* Complaint header */}
          <div className="glass-card p-6">
            <div className="flex items-start justify-between gap-4 mb-4">
              <h1 className="text-xl font-bold text-gray-100">{complaint.title}</h1>
              <div className="flex items-center gap-2 shrink-0">
                <StatusBadge status={complaint.status} size="md" />
                <PriorityBadge priority={complaint.priority} />
              </div>
            </div>

            <p className="text-gray-400 leading-relaxed whitespace-pre-wrap">
              {complaint.description}
            </p>

            {/* Metadata */}
            <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-gray-800/60">
              <MetaItem label="Submitted" value={new Date(complaint.created_at).toLocaleDateString()} />
              <MetaItem label="Updated" value={new Date(complaint.updated_at).toLocaleDateString()} />
              <MetaItem
                label="Customer"
                value={complaint.customer?.name || '—'}
              />
              <MetaItem
                label="Assigned Agent"
                value={complaint.assigned_agent?.name || 'Unassigned'}
              />
            </div>

            {complaint.resolved_at && (
              <div className="mt-3 pt-3 border-t border-gray-800/60">
                <MetaItem label="Resolved At" value={new Date(complaint.resolved_at).toLocaleString()} />
              </div>
            )}
          </div>


          {/* AI Suggestion Panel — visible to AGENT and ADMIN only */}
          {(user?.role === 'AGENT' || user?.role === 'ADMIN') && (
            <AiSuggestionPanel complaintId={complaint.id} />
          )}

          {/* Timeline */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-gray-200 mb-5">Status Timeline</h2>
            <Timeline history={history} />
          </div>
        </div>

        {/* ── Right column: actions ──────────────────────────── */}
        <div className="space-y-6">
          {/* Status update */}
          {canUpdateStatus && (
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Update Status</h3>
              <div className="space-y-3">
                <div className="flex gap-2 flex-wrap">
                  {agentTransitions.map((s) => (
                    <button
                      key={s}
                      onClick={() => setNewStatus(s === newStatus ? '' : s)}
                      className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all duration-200 ${
                        newStatus === s
                          ? 'bg-blue-500/15 text-blue-400 border-blue-500/30'
                          : 'bg-gray-800/40 text-gray-500 border-gray-700/40 hover:text-gray-300'
                      }`}
                    >
                      {s.replace('_', ' ')}
                    </button>
                  ))}
                </div>
                {newStatus && (
                  <div className="space-y-3 animate-fade-in">
                    <textarea
                      value={statusComment}
                      onChange={(e) => setStatusComment(e.target.value)}
                      className="input-field text-sm min-h-[80px]"
                      placeholder="Add a comment (optional)"
                    />
                    <button
                      onClick={handleStatusUpdate}
                      disabled={statusLoading}
                      className="btn-primary w-full text-sm flex items-center justify-center gap-2"
                    >
                      {statusLoading ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      ) : (
                        `Move to ${newStatus.replace('_', ' ')}`
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Assignment (admin only) */}
          {canAssign && (
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">
                {complaint.assigned_agent ? 'Reassign Agent' : 'Assign Agent'}
              </h3>
              <div className="space-y-3">
                <select
                  value={selectedAgent}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  className="input-field text-sm"
                >
                  <option value="">Select an agent...</option>
                  {agents.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.email})
                    </option>
                  ))}
                </select>

                {selectedAgent && (
                  <div className="space-y-3 animate-fade-in">
                    <textarea
                      value={assignComment}
                      onChange={(e) => setAssignComment(e.target.value)}
                      className="input-field text-sm min-h-[80px]"
                      placeholder="Assignment note (optional)"
                    />
                    <button
                      onClick={handleAssign}
                      disabled={assignLoading}
                      className="btn-primary w-full text-sm flex items-center justify-center gap-2"
                    >
                      {assignLoading ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      ) : (
                        'Assign Agent'
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Complaint info sidebar */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">Details</h3>
            <div className="space-y-3">
              <SidebarItem label="ID" value={complaint.id.slice(0, 8) + '...'} />
              <SidebarItem label="Status" value={complaint.status.replace('_', ' ')} />
              <SidebarItem label="Priority" value={complaint.priority} />
              <SidebarItem
                label="Customer"
                value={complaint.customer ? `${complaint.customer.name} (${complaint.customer.email})` : '—'}
              />
              <SidebarItem
                label="Agent"
                value={complaint.assigned_agent ? `${complaint.assigned_agent.name}` : 'Unassigned'}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500 font-medium">{label}</p>
      <p className="text-sm text-gray-300 mt-0.5">{value}</p>
    </div>
  );
}

function SidebarItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-gray-500">{label}</span>
      <span className="text-xs text-gray-300 font-medium">{value}</span>
    </div>
  );
}
