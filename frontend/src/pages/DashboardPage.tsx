import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getErrorMessage } from '../api/client';
import { fetchHealth } from '../api/employees';
import { useAuth } from '../context/AuthContext';
import { Badge, Card, Spinner } from '../components/ui';
import { HealthData } from '../types';

export function DashboardPage() {
  const { user, canViewEmployees } = useAuth();
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const roleColor = {
    ADMIN: 'purple' as const,
    MANAGER: 'blue' as const,
    EMPLOYEE: 'green' as const,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Hello, {user?.full_name?.split(' ')[0]} 👋
        </h1>
        <p className="mt-1 text-slate-600">Welcome to the Employee Management System</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="p-6">
          <p className="text-sm font-medium text-slate-500">Your Role</p>
          <div className="mt-2">
            {user && <Badge color={roleColor[user.role]}>{user.role}</Badge>}
          </div>
          <p className="mt-3 text-sm text-slate-600">{user?.email}</p>
        </Card>

        {canViewEmployees && (
          <Card className="p-6">
            <p className="text-sm font-medium text-slate-500">Quick Action</p>
            <Link
              to="/employees"
              className="mt-2 inline-block text-lg font-semibold text-brand-600 hover:text-brand-700"
            >
              Manage Employees →
            </Link>
            <p className="mt-2 text-sm text-slate-600">
              View, create, and update employee records
            </p>
          </Card>
        )}

        {!canViewEmployees && (
          <Card className="p-6">
            <p className="text-sm font-medium text-slate-500">Access Level</p>
            <p className="mt-2 text-sm text-slate-600">
              You can view your own employee profile. Contact an admin to link your account.
            </p>
          </Card>
        )}

        <Card className="p-6">
          <p className="text-sm font-medium text-slate-500">System Status</p>
          {loading ? (
            <Spinner />
          ) : error ? (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          ) : health ? (
            <div className="mt-3 space-y-2">
              <StatusRow label="Application" healthy={health.application.healthy} />
              <StatusRow label="MongoDB" healthy={health.mongodb.healthy} />
              <StatusRow label="Redis" healthy={health.redis.healthy} />
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}

function StatusRow({ label, healthy }: { label: string; healthy: boolean }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-slate-600">{label}</span>
      <Badge color={healthy ? 'green' : 'red'}>{healthy ? 'Healthy' : 'Down'}</Badge>
    </div>
  );
}
