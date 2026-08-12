/* ── TypeScript interfaces — mirrors backend Pydantic schemas ── */

// ── Users ──────────────────────────────────────────────────────

export type UserRole = 'CUSTOMER' | 'AGENT' | 'ADMIN';

export interface UserResponse {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
  role: 'AGENT' | 'ADMIN';
}

export interface UpdateUserRequest {
  name?: string;
  is_active?: boolean;
}

// ── Auth ───────────────────────────────────────────────────────

export interface LoginRequest {
  username: string; // OAuth2 spec — actually the email
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// ── Complaints ─────────────────────────────────────────────────

export type ComplaintStatus = 'SUBMITTED' | 'ASSIGNED' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
export type ComplaintPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface ComplaintCreate {
  title: string;
  description: string;
  priority: ComplaintPriority;
}

export interface ComplaintResponse {
  id: string;
  customer_id: string;
  assigned_agent_id: string | null;
  title: string;
  description: string;
  status: ComplaintStatus;
  priority: ComplaintPriority;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  customer: UserResponse | null;
  assigned_agent: UserResponse | null;
}

export interface ComplaintListResponse {
  id: string;
  title: string;
  status: ComplaintStatus;
  priority: ComplaintPriority;
  assigned_agent_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface StatusUpdateRequest {
  status: string;
  comment?: string;
}

export interface AssignRequest {
  agent_id: string;
  comment?: string;
}

export interface StatusHistoryResponse {
  id: string;
  old_status: string | null;
  new_status: string;
  changed_by: UserResponse;
  comment: string | null;
  created_at: string;
}

// ── Dashboards ─────────────────────────────────────────────────

export interface CustomerDashboard {
  total_complaints: number;
  open_complaints: number;
  resolved_complaints: number;
  recent_complaints: ComplaintListResponse[];
}

export interface AgentDashboard {
  total_assigned: number;
  pending: number;
  in_progress: number;
  resolved: number;
  recent_assignments: ComplaintListResponse[];
}

export interface AgentPerformance {
  agent: UserResponse;
  total_assigned: number;
  total_resolved: number;
  total_open: number;
  resolution_rate: number;
  avg_resolution_hours: number | null;
}

export interface AdminDashboard {
  total_complaints: number;
  submitted: number;
  assigned: number;
  in_progress: number;
  resolved: number;
  closed: number;
  unassigned: number;
  total_agents: number;
  active_agents: number;
  agent_performance: AgentPerformance[];
}

// ── State machine ──────────────────────────────────────────────

export const VALID_TRANSITIONS: Record<ComplaintStatus, ComplaintStatus[]> = {
  SUBMITTED: ['ASSIGNED'],
  ASSIGNED: ['IN_PROGRESS'],
  IN_PROGRESS: ['RESOLVED'],
  RESOLVED: ['CLOSED', 'IN_PROGRESS'],
  CLOSED: [],
};
