import { useEffect, useState } from 'react';
import client from '../../api/client';
import type { UserResponse } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function UserManagement() {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  // Create form
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'AGENT' | 'ADMIN'>('AGENT');
  const [createError, setCreateError] = useState('');
  const [createLoading, setCreateLoading] = useState(false);

  // Edit modal
  const [editUser, setEditUser] = useState<UserResponse | null>(null);
  const [editName, setEditName] = useState('');
  const [editActive, setEditActive] = useState(true);
  const [editLoading, setEditLoading] = useState(false);

  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    fetchUsers();
  }, [roleFilter]);

  const fetchUsers = async () => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (roleFilter) params.role = roleFilter;
    try {
      const res = await client.get('/users', { params });
      setUsers(res.data);
    } catch {}
    setLoading(false);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError('');
    setCreateLoading(true);
    try {
      await client.post('/users', { name, email, password, role });
      setShowCreate(false);
      setName(''); setEmail(''); setPassword('');
      setSuccessMsg(`${role} account created successfully.`);
      setTimeout(() => setSuccessMsg(''), 4000);
      fetchUsers();
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setCreateLoading(false);
    }
  };

  const openEdit = (u: UserResponse) => {
    setEditUser(u);
    setEditName(u.name);
    setEditActive(u.is_active);
  };

  const handleUpdate = async () => {
    if (!editUser) return;
    setEditLoading(true);
    try {
      await client.put(`/users/${editUser.id}`, {
        name: editName || undefined,
        is_active: editActive,
      });
      setEditUser(null);
      setSuccessMsg('User updated.');
      setTimeout(() => setSuccessMsg(''), 4000);
      fetchUsers();
    } catch {}
    setEditLoading(false);
  };

  const roleBadgeColors: Record<string, string> = {
    CUSTOMER: 'bg-emerald-500/15 text-emerald-400',
    AGENT: 'bg-purple-500/15 text-purple-400',
    ADMIN: 'bg-amber-500/15 text-amber-400',
  };

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">User Management</h1>
          <p className="text-gray-500 text-sm mt-1">Create and manage system accounts</p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="btn-primary text-sm inline-flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Create User
        </button>
      </div>

      {/* Success message */}
      {successMsg && (
        <div className="mb-4 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm animate-fade-in">
          ✓ {successMsg}
        </div>
      )}

      {/* Create form */}
      {showCreate && (
        <div className="glass-card p-6 mb-6 animate-fade-in">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Create New Account</h3>
          {createError && (
            <div className="mb-3 px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {createError}
            </div>
          )}
          <form onSubmit={handleCreate} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <input
              type="text" value={name} onChange={(e) => setName(e.target.value)}
              className="input-field text-sm" placeholder="Full name" required minLength={2}
            />
            <input
              type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              className="input-field text-sm" placeholder="Email address" required
            />
            <input
              type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="input-field text-sm" placeholder="Password (min 6 chars)" required minLength={6}
            />
            <select
              value={role} onChange={(e) => setRole(e.target.value as 'AGENT' | 'ADMIN')}
              className="input-field text-sm"
            >
              <option value="AGENT">Agent</option>
              <option value="ADMIN">Admin</option>
            </select>
            <div className="sm:col-span-2 flex gap-3">
              <button type="submit" disabled={createLoading} className="btn-primary text-sm">
                {createLoading ? 'Creating...' : 'Create Account'}
              </button>
              <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary text-sm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Role filter */}
      <div className="flex gap-2 mb-6">
        {['', 'CUSTOMER', 'AGENT', 'ADMIN'].map((r) => (
          <button
            key={r}
            onClick={() => setRoleFilter(r)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all duration-200 ${
              roleFilter === r
                ? 'bg-blue-500/15 text-blue-400 border-blue-500/30'
                : 'bg-gray-800/40 text-gray-500 border-gray-700/40 hover:text-gray-300'
            }`}
          >
            {r || 'All'}
          </button>
        ))}
      </div>

      {/* Users table */}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="font-medium text-gray-200">{u.name}</td>
                  <td className="text-gray-400">{u.email}</td>
                  <td>
                    <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${roleBadgeColors[u.role] || ''}`}>
                      {u.role}
                    </span>
                  </td>
                  <td>
                    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${
                      u.is_active ? 'text-emerald-400' : 'text-red-400'
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${u.is_active ? 'bg-emerald-400' : 'bg-red-400'}`} />
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="text-sm text-gray-500">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      onClick={() => openEdit(u)}
                      className="text-xs text-blue-400 hover:text-blue-300 font-medium transition-colors"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Edit modal */}
      {editUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="glass-card p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Edit User</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Name</label>
                <input
                  type="text" value={editName} onChange={(e) => setEditName(e.target.value)}
                  className="input-field text-sm"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-400">Active Status</label>
                <button
                  type="button"
                  onClick={() => setEditActive(!editActive)}
                  className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${
                    editActive ? 'bg-emerald-600' : 'bg-gray-700'
                  }`}
                >
                  <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${
                    editActive ? 'translate-x-5' : 'translate-x-0'
                  }`} />
                </button>
              </div>
              <div className="flex gap-3 pt-2">
                <button onClick={handleUpdate} disabled={editLoading} className="btn-primary text-sm flex-1">
                  {editLoading ? 'Saving...' : 'Save Changes'}
                </button>
                <button onClick={() => setEditUser(null)} className="btn-secondary text-sm">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
