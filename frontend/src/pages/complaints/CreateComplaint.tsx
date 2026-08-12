import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import type { ComplaintPriority } from '../../types';

const PRIORITIES: { value: ComplaintPriority; label: string; desc: string }[] = [
  { value: 'LOW', label: 'Low', desc: 'Minor issue, no urgency' },
  { value: 'MEDIUM', label: 'Medium', desc: 'Normal priority' },
  { value: 'HIGH', label: 'High', desc: 'Urgent attention needed' },
  { value: 'CRITICAL', label: 'Critical', desc: 'Business-critical, immediate action' },
];

export default function CreateComplaint() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<ComplaintPriority>('MEDIUM');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await client.post('/complaints', { title, description, priority });
      setSuccess(true);
      setTimeout(() => navigate('/complaints'), 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit complaint');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="animate-fade-in flex flex-col items-center justify-center py-20">
        <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-gray-100">Complaint Submitted!</h2>
        <p className="text-gray-500 text-sm mt-1">You'll receive an email confirmation shortly.</p>
      </div>
    );
  }

  return (
    <div className="animate-fade-in max-w-2xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-100">Submit a Complaint</h1>
        <p className="text-gray-500 text-sm mt-1">Describe your issue and we'll assign an agent to help.</p>
      </div>

      {error && (
        <div className="mb-4 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="glass-card p-6 space-y-6">
        {/* Title */}
        <div>
          <label htmlFor="complaint-title" className="block text-sm font-medium text-gray-400 mb-1.5">
            Title <span className="text-gray-600">(min 5 chars)</span>
          </label>
          <input
            id="complaint-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input-field"
            placeholder="Brief summary of your issue"
            required
            minLength={5}
            maxLength={500}
            autoFocus
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="complaint-desc" className="block text-sm font-medium text-gray-400 mb-1.5">
            Description <span className="text-gray-600">(min 10 chars)</span>
          </label>
          <textarea
            id="complaint-desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input-field min-h-[140px] resize-y"
            placeholder="Provide details about the issue, including any relevant dates, product models, or reference numbers..."
            required
            minLength={10}
          />
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Priority</label>
          <div className="grid grid-cols-2 gap-3">
            {PRIORITIES.map((p) => (
              <label
                key={p.value}
                className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all duration-200 ${
                  priority === p.value
                    ? 'bg-blue-500/10 border-blue-500/30'
                    : 'bg-gray-800/30 border-gray-700/40 hover:border-gray-600/60'
                }`}
              >
                <input
                  type="radio"
                  name="priority"
                  value={p.value}
                  checked={priority === p.value}
                  onChange={() => setPriority(p.value)}
                  className="mt-0.5 accent-blue-500"
                />
                <div>
                  <p className="text-sm font-medium text-gray-200">{p.label}</p>
                  <p className="text-xs text-gray-500">{p.desc}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Submit */}
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Submitting...
              </>
            ) : (
              'Submit Complaint'
            )}
          </button>
          <button
            type="button"
            onClick={() => navigate('/complaints')}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
