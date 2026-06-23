import { useCallback, useEffect, useState } from 'react';
import { getErrorMessage } from '../api/client';
import {
  createEmployee,
  deleteEmployee,
  fetchEmployees,
  updateEmployee,
} from '../api/employees';
import { useAuth } from '../context/AuthContext';
import { EmployeeForm } from '../components/EmployeeForm';
import { Modal } from '../components/Modal';
import { Alert, Badge, Button, Card, Input, Select, Spinner } from '../components/ui';
import { Employee, EmployeeFormData } from '../types';

const SORT_OPTIONS = [
  { value: 'created_at', label: 'Newest First' },
  { value: 'name', label: 'Name (A-Z)' },
  { value: 'department', label: 'Department' },
  { value: 'salary', label: 'Salary' },
];

export function EmployeesPage() {
  const { canCreateEmployee, canUpdateEmployee, canDeleteEmployee } = useAuth();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('');
  const [sort, setSort] = useState('created_at');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Employee | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<Employee | null>(null);

  const loadEmployees = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchEmployees({
        page,
        limit,
        search: search || undefined,
        department: department || undefined,
        sort,
      });
      setEmployees(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [page, limit, search, department, sort]);

  useEffect(() => {
    loadEmployees();
  }, [loadEmployees]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadEmployees();
  };

  const openCreate = () => {
    setEditing(null);
    setModalOpen(true);
  };

  const openEdit = (emp: Employee) => {
    setEditing(emp);
    setModalOpen(true);
  };

  const handleSubmit = async (data: EmployeeFormData) => {
    setSubmitting(true);
    try {
      if (editing) {
        await updateEmployee(editing.id, data);
        setSuccess('Employee updated successfully');
      } else {
        await createEmployee(data);
        setSuccess('Employee created successfully');
      }
      setModalOpen(false);
      await loadEmployees();
    } catch (err) {
      throw new Error(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm) return;
    setSubmitting(true);
    try {
      await deleteEmployee(deleteConfirm.id);
      setSuccess('Employee deleted successfully');
      setDeleteConfirm(null);
      await loadEmployees();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const formatSalary = (n: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Employees</h1>
          <p className="text-sm text-slate-600">{total} total employees</p>
        </div>
        {canCreateEmployee && (
          <Button onClick={openCreate}>+ Add Employee</Button>
        )}
      </div>

      {error && <Alert message={error} />}
      {success && (
        <Alert message={success} type="success" />
      )}

      <Card className="p-4">
        <form onSubmit={handleSearch} className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <Input
              label="Search"
              placeholder="Search by name, email, department..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-40">
            <Input
              label="Department"
              placeholder="e.g. IT"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-44">
            <Select
              label="Sort by"
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              options={SORT_OPTIONS}
            />
          </div>
          <Button type="submit" variant="secondary">
            Apply
          </Button>
        </form>
      </Card>

      <Card className="overflow-hidden">
        {loading ? (
          <Spinner />
        ) : employees.length === 0 ? (
          <div className="py-16 text-center text-slate-500">No employees found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50">
                <tr>
                  <th className="px-4 py-3 font-medium text-slate-600">Name</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Email</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Department</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Designation</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Salary</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {employees.map((emp) => (
                  <tr key={emp.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-900">{emp.name}</td>
                    <td className="px-4 py-3 text-slate-600">{emp.email}</td>
                    <td className="px-4 py-3">
                      <Badge color="blue">{emp.department}</Badge>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{emp.designation}</td>
                    <td className="px-4 py-3 text-slate-900">{formatSalary(emp.salary)}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        {canUpdateEmployee && (
                          <Button size="sm" variant="ghost" onClick={() => openEdit(emp)}>
                            Edit
                          </Button>
                        )}
                        {canDeleteEmployee && (
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-red-600 hover:bg-red-50"
                            onClick={() => setDeleteConfirm(emp)}
                          >
                            Delete
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {pages > 1 && (
          <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3">
            <p className="text-sm text-slate-600">
              Page {page} of {pages}
            </p>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <Button
                size="sm"
                variant="secondary"
                disabled={page >= pages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </Card>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Edit Employee' : 'Add Employee'}
      >
        <EmployeeForm
          initial={editing}
          onSubmit={handleSubmit}
          onCancel={() => setModalOpen(false)}
          loading={submitting}
        />
      </Modal>

      <Modal
        open={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title="Confirm Delete"
      >
        <p className="mb-4 text-sm text-slate-600">
          Are you sure you want to delete <strong>{deleteConfirm?.name}</strong>? This is a soft
          delete and can be restored from the database.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteConfirm(null)}>
            Cancel
          </Button>
          <Button variant="danger" loading={submitting} onClick={handleDelete}>
            Delete
          </Button>
        </div>
      </Modal>
    </div>
  );
}
