import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getErrorMessage } from '../api/client';
import { fetchDashboardAnalytics } from '../api/analytics';
import { fetchHealth } from '../api/employees';
import { useAuth } from '../context/AuthContext';
import { Badge, Card, Spinner } from '../components/ui';
import { DashboardAnalytics, HealthData } from '../types';

export function DashboardPage() {
  const { user, canViewEmployees } = useAuth();
  const [health, setHealth] = useState<HealthData | null>(null);
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const promises: Promise<void>[] = [
      fetchHealth()
        .then(setHealth)
        .catch((err) => setError(getErrorMessage(err))),
    ];
    if (canViewEmployees) {
      promises.push(
        fetchDashboardAnalytics()
          .then(setAnalytics)
          .catch(() => {})
      );
    }
    Promise.all(promises).finally(() => setLoading(false));
  }, [canViewEmployees]);

  const roleColor = {
    ADMIN: 'purple' as const,
    MANAGER: 'blue' as const,
    EMPLOYEE: 'green' as const,
  };

  const formatSalary = (n: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Hello, {user?.full_name?.split(' ')[0]} 👋
        </h1>
        <p className="mt-1 text-slate-600">Welcome to the Employee Management System</p>
      </div>

      {canViewEmployees && analytics && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total Employees" value={String(analytics.total_employees)} />
          <StatCard label="Departments" value={String(analytics.total_departments)} />
          <StatCard label="Avg Salary" value={formatSalary(analytics.average_salary)} />
          <StatCard label="New Hires (Month)" value={String(analytics.new_hires_this_month)} />
        </div>
      )}

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="p-6">
          <p className="text-sm font-medium text-slate-500">Your Role</p>
          <div className="mt-2">
            {user && <Badge color={roleColor[user.role]}>{user.role}</Badge>}
          </div>
          <p className="mt-3 text-sm text-slate-600">{user?.email}</p>
          <Link to="/profile" className="mt-3 inline-block text-sm font-medium text-brand-600 hover:text-brand-700">
            View Profile →
          </Link>
        </Card>

        {canViewEmployees && (
          <Card className="p-6">
            <p className="text-sm font-medium text-slate-500">Quick Actions</p>
            <div className="mt-3 space-y-2">
              <Link to="/employees" className="block text-sm font-semibold text-brand-600 hover:text-brand-700">
                Manage Employees →
              </Link>
              <Link to="/org-chart" className="block text-sm font-semibold text-brand-600 hover:text-brand-700">
                Org Chart →
              </Link>
              <Link to="/departments" className="block text-sm font-semibold text-brand-600 hover:text-brand-700">
                Departments →
              </Link>
            </div>
          </Card>
        )}

        {!canViewEmployees && (
          <Card className="p-6">
            <p className="text-sm font-medium text-slate-500">Access Level</p>
            <p className="mt-2 text-sm text-slate-600">
              You can view your own employee profile. Contact an admin to link your account.
            </p>
            <Link to="/profile" className="mt-3 inline-block text-sm font-medium text-brand-600 hover:text-brand-700">
              My Profile →
            </Link>
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

      {canViewEmployees && analytics && analytics.employees_by_department.length > 0 && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Employees by Department</h2>
            <div className="space-y-3">
              {analytics.employees_by_department.map((item) => (
                <div key={item.department} className="flex items-center justify-between">
                  <span className="text-sm text-slate-700">{item.department}</span>
                  <div className="flex items-center gap-3">
                    <div className="h-2 rounded-full bg-brand-100" style={{ width: `${Math.min(item.count * 20, 120)}px` }}>
                      <div className="h-2 rounded-full bg-brand-600" style={{ width: '100%' }} />
                    </div>
                    <Badge color="blue">{item.count}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Recent Activity</h2>
            {analytics.recent_activity.length === 0 ? (
              <p className="text-sm text-slate-500">No recent activity</p>
            ) : (
              <ul className="space-y-3">
                {analytics.recent_activity.map((activity, i) => (
                  <li key={i} className="flex items-start justify-between text-sm">
                    <div>
                      <Badge color="purple">{activity.action}</Badge>
                      <p className="mt-1 text-slate-500">{activity.resource}</p>
                    </div>
                    <span className="text-xs text-slate-400">
                      {new Date(activity.timestamp).toLocaleString()}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-5">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
    </Card>
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
