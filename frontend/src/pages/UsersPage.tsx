import { useCallback, useEffect, useState } from 'react';
import { getErrorMessage } from '../api/client';
import { fetchEmployees } from '../api/employees';
import { fetchUsers, updateUser } from '../api/users';
import { Alert, Badge, Button, Card, Input, Select, Spinner } from '../components/ui';
import { Role, UserRecord } from '../types';

const ROLE_OPTIONS = [
  { value: '', label: 'All Roles' },
  { value: 'ADMIN', label: 'Admin' },
  { value: 'MANAGER', label: 'Manager' },
  { value: 'EMPLOYEE', label: 'Employee' },
];

export function UsersPage() {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [employees, setEmployees] = useState<{ value: string; label: string }[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [savingId, setSavingId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchUsers({
        page,
        limit: 10,
        search: search || undefined,
        role: (roleFilter as Role) || undefined,
      });
      setUsers(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [page, search, roleFilter]);

  useEffect(() => {
    load();
    fetchEmployees({ page: 1, limit: 100 })
      .then((data) =>
        setEmployees(data.items.map((e) => ({ value: e.id, label: `${e.name} (${e.email})` })))
      )
      .catch(() => setEmployees([]));
  }, [load]);

  const handleRoleChange = async (userId: string, role: Role) => {
    setSavingId(userId);
    setError('');
    try {
      await updateUser(userId, { role });
      setSuccess('User role updated');
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSavingId(null);
    }
  };

  const handleEmployeeLink = async (userId: string, employeeId: string) => {
    setSavingId(userId);
    setError('');
    try {
      await updateUser(userId, { employee_id: employeeId || null });
      setSuccess('Employee link updated');
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSavingId(null);
    }
  };

  const handleToggleActive = async (user: UserRecord) => {
    setSavingId(user.id);
    setError('');
    try {
      await updateUser(user.id, { is_active: !user.is_active });
      setSuccess(user.is_active ? 'User deactivated' : 'User activated');
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">User Management</h1>
        <p className="text-sm text-slate-600">{total} users</p>
      </div>

      {error && <Alert message={error} />}
      {success && <Alert message={success} type="success" />}

      <Card className="p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <Input label="Search" placeholder="Email or name..." value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <div className="w-full sm:w-40">
            <Select label="Role" value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)} options={ROLE_OPTIONS} />
          </div>
          <Button variant="secondary" onClick={() => { setPage(1); load(); }}>Apply</Button>
        </div>
      </Card>

      <Card className="overflow-hidden">
        {loading ? (
          <Spinner />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50">
                <tr>
                  <th className="px-4 py-3 font-medium text-slate-600">User</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Role</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Linked Employee</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Status</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-900">{user.full_name}</p>
                      <p className="text-slate-500">{user.email}</p>
                    </td>
                    <td className="px-4 py-3">
                      <Select
                        value={user.role}
                        onChange={(e) => handleRoleChange(user.id, e.target.value as Role)}
                        options={[
                          { value: 'ADMIN', label: 'Admin' },
                          { value: 'MANAGER', label: 'Manager' },
                          { value: 'EMPLOYEE', label: 'Employee' },
                        ]}
                        disabled={savingId === user.id}
                      />
                    </td>
                    <td className="px-4 py-3">
                      <Select
                        value={user.employee_id || ''}
                        onChange={(e) => handleEmployeeLink(user.id, e.target.value)}
                        options={[{ value: '', label: 'None' }, ...employees]}
                        disabled={savingId === user.id}
                      />
                    </td>
                    <td className="px-4 py-3">
                      <Badge color={user.is_active ? 'green' : 'red'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Button
                        size="sm"
                        variant="ghost"
                        loading={savingId === user.id}
                        onClick={() => handleToggleActive(user)}
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
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
