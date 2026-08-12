import { useAuth } from '../../contexts/AuthContext';
import CustomerDashboard from './CustomerDashboard';
import AgentDashboard from './AgentDashboard';
import AdminDashboard from './AdminDashboard';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function DashboardRouter() {
  const { user } = useAuth();

  if (!user) return <LoadingSpinner />;

  switch (user.role) {
    case 'CUSTOMER':
      return <CustomerDashboard />;
    case 'AGENT':
      return <AgentDashboard />;
    case 'ADMIN':
      return <AdminDashboard />;
    default:
      return <CustomerDashboard />;
  }
}
