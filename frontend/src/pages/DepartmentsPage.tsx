import { FormEvent, useCallback, useEffect, useState } from 'react';
import { getErrorMessage } from '../api/client';
import {
  createDepartment,
  deleteDepartment,
  fetchDepartments,
  updateDepartment,
} from '../api/departments';
import { useAuth } from '../context/AuthContext';
import { Modal } from '../components/Modal';
import { Alert, Badge, Button, Card, Input, Spinner } from '../components/ui';
import { Department, DepartmentFormData } from '../types';

export function DepartmentsPage() {
  const { hasRole } = useAuth();
  const isAdmin = hasRole('ADMIN');
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Department | null>(null);
  const [form, setForm] = useState<DepartmentFormData>({ name: '', description: '' });
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<Department | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setDepartments(await fetchDepartments());
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', description: '' });
    setModalOpen(true);
  };

  const openEdit = (dept: Department) => {
    setEditing(dept);
    setForm({ name: dept.name, description: dept.description || '' });
    setModalOpen(true);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      if (editing) {
        await updateDepartment(editing.id, form);
        setSuccess('Department updated');
      } else {
        await createDepartment(form);
        setSuccess('Department created');
      }
      setModalOpen(false);
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm) return;
    setSubmitting(true);
    try {
      await deleteDepartment(deleteConfirm.id);
      setSuccess('Department deleted');
      setDeleteConfirm(null);
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Departments</h1>
          <p className="text-sm text-slate-600">{departments.length} departments</p>
        </div>
        {isAdmin && <Button onClick={openCreate}>+ Add Department</Button>}
      </div>

      {error && <Alert message={error} />}
      {success && <Alert message={success} type="success" />}

      <Card className="overflow-hidden">
        {loading ? (
          <Spinner />
        ) : departments.length === 0 ? (
          <div className="py-16 text-center text-slate-500">No departments yet</div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                <th className="px-4 py-3 font-medium text-slate-600">Name</th>
                <th className="px-4 py-3 font-medium text-slate-600">Description</th>
                <th className="px-4 py-3 font-medium text-slate-600">Employees</th>
                {isAdmin && <th className="px-4 py-3 font-medium text-slate-600">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {departments.map((dept) => (
                <tr key={dept.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{dept.name}</td>
                  <td className="px-4 py-3 text-slate-600">{dept.description || '—'}</td>
                  <td className="px-4 py-3">
                    <Badge color="blue">{dept.employee_count}</Badge>
                  </td>
                  {isAdmin && (
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <Button size="sm" variant="ghost" onClick={() => openEdit(dept)}>
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-red-600"
                          onClick={() => setDeleteConfirm(dept)}
                        >
                          Delete
                        </Button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Department' : 'Add Department'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <Input label="Description" value={form.description || ''} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <div className="flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" loading={submitting}>{editing ? 'Update' : 'Create'}</Button>
          </div>
        </form>
      </Modal>

      <Modal open={!!deleteConfirm} onClose={() => setDeleteConfirm(null)} title="Confirm Delete">
        <p className="mb-4 text-sm text-slate-600">Delete department <strong>{deleteConfirm?.name}</strong>?</p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteConfirm(null)}>Cancel</Button>
          <Button variant="danger" loading={submitting} onClick={handleDelete}>Delete</Button>
        </div>
      </Modal>
    </div>
  );
}
