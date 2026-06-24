import { useCallback, useEffect, useState } from 'react';
import { getErrorMessage } from '../api/client';
import { fetchAuditLogs } from '../api/audit';
import { Alert, Badge, Button, Card, Input, Select, Spinner } from '../components/ui';
import { AuditLog } from '../types';

const ACTION_OPTIONS = [
  { value: '', label: 'All Actions' },
  { value: 'LOGIN', label: 'Login' },
  { value: 'LOGOUT', label: 'Logout' },
  { value: 'CREATE_EMPLOYEE', label: 'Create Employee' },
  { value: 'UPDATE_EMPLOYEE', label: 'Update Employee' },
  { value: 'DELETE_EMPLOYEE', label: 'Delete Employee' },
  { value: 'ROLE_CHANGE', label: 'Role Change' },
  { value: 'CREATE_DEPARTMENT', label: 'Create Department' },
  { value: 'PASSWORD_RESET', label: 'Password Reset' },
  { value: 'BULK_IMPORT_EMPLOYEES', label: 'Bulk Import' },
];

export function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const [action, setAction] = useState('');
  const [userId, setUserId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAuditLogs({
        page,
        limit: 20,
        action: action || undefined,
        user_id: userId || undefined,
      });
      setLogs(data.items);
      setPages(data.pages);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [page, action, userId]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Audit Logs</h1>
        <p className="text-sm text-slate-600">System activity and compliance trail</p>
      </div>

      {error && <Alert message={error} />}

      <Card className="p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="w-full sm:w-48">
            <Select label="Action" value={action} onChange={(e) => setAction(e.target.value)} options={ACTION_OPTIONS} />
          </div>
          <div className="flex-1">
            <Input label="User ID" placeholder="Filter by user ID..." value={userId} onChange={(e) => setUserId(e.target.value)} />
          </div>
          <Button variant="secondary" onClick={() => { setPage(1); load(); }}>Apply</Button>
        </div>
      </Card>

      <Card className="overflow-hidden">
        {loading ? (
          <Spinner />
        ) : logs.length === 0 ? (
          <div className="py-16 text-center text-slate-500">No audit logs found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50">
                <tr>
                  <th className="px-4 py-3 font-medium text-slate-600">Timestamp</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Action</th>
                  <th className="px-4 py-3 font-medium text-slate-600">User</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Resource</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-slate-600">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-4 py-3">
                      <Badge color="purple">{log.action}</Badge>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-600">{log.user_id.slice(-8)}</td>
                    <td className="px-4 py-3 text-slate-600">
                      {log.resource}
                      {log.resource_id && (
                        <span className="ml-1 font-mono text-xs">({log.resource_id.slice(-8)})</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {pages > 1 && (
          <div className="flex items-center justify-between border-t px-4 py-3">
            <p className="text-sm text-slate-600">Page {page} of {pages}</p>
            <div className="flex gap-2">
              <Button size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</Button>
              <Button size="sm" variant="secondary" disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>Next</Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
