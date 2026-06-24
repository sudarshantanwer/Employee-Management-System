import { FormEvent, useEffect, useState } from 'react';
import { fetchDepartments } from '../api/departments';
import { fetchEmployees } from '../api/employees';
import { Employee, EmployeeFormData } from '../types';
import { Button, Input, Select } from './ui';

interface EmployeeFormProps {
  initial?: Employee | null;
  onSubmit: (data: EmployeeFormData) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

export function EmployeeForm({ initial, onSubmit, onCancel, loading }: EmployeeFormProps) {
  const [form, setForm] = useState<EmployeeFormData>({
    name: '',
    email: '',
    department: '',
    designation: '',
    salary: 0,
  });
  const [departments, setDepartments] = useState<{ value: string; label: string }[]>([]);
  const [managers, setManagers] = useState<{ value: string; label: string }[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDepartments()
      .then((depts) =>
        setDepartments(depts.map((d) => ({ value: d.name, label: d.name })))
      )
      .catch(() => setDepartments([]));

    fetchEmployees({ page: 1, limit: 100 })
      .then((data) =>
        setManagers(
          data.items
            .filter((e) => e.id !== initial?.id)
            .map((e) => ({ value: e.id, label: `${e.name} (${e.designation})` }))
        )
      )
      .catch(() => setManagers([]));
  }, [initial?.id]);

  useEffect(() => {
    if (initial) {
      setForm({
        name: initial.name,
        email: initial.email,
        department: initial.department,
        designation: initial.designation,
        salary: initial.salary,
        manager_id: initial.manager_id || undefined,
        phone: initial.phone || undefined,
        address: initial.address || undefined,
        emergency_contact: initial.emergency_contact || undefined,
      });
    } else if (departments.length > 0 && !form.department) {
      setForm((f) => ({ ...f, department: departments[0].value }));
    }
  }, [initial, departments]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (!form.name || !form.email || !form.designation || !form.department || form.salary <= 0) {
      setError('Please fill in all required fields with valid values.');
      return;
    }
    try {
      await onSubmit(form);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save employee');
    }
  };

  const deptOptions =
    departments.length > 0
      ? departments
      : [{ value: form.department || 'General', label: form.department || 'General' }];

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}
      <div className="grid gap-4 sm:grid-cols-2">
        <Input
          label="Full Name"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          required
        />
        <Input
          label="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          required
        />
        <Select
          label="Department"
          value={form.department}
          onChange={(e) => setForm({ ...form, department: e.target.value })}
          options={deptOptions}
        />
        <Input
          label="Designation"
          value={form.designation}
          onChange={(e) => setForm({ ...form, designation: e.target.value })}
          required
        />
        <Input
          label="Salary"
          type="number"
          min={1}
          step={1000}
          value={form.salary || ''}
          onChange={(e) => setForm({ ...form, salary: Number(e.target.value) })}
          required
        />
        <Select
          label="Manager"
          value={form.manager_id || ''}
          onChange={(e) =>
            setForm({ ...form, manager_id: e.target.value || undefined })
          }
          options={[{ value: '', label: 'None' }, ...managers]}
        />
        <Input
          label="Phone"
          value={form.phone || ''}
          onChange={(e) => setForm({ ...form, phone: e.target.value || undefined })}
        />
        <Input
          label="Emergency Contact"
          value={form.emergency_contact || ''}
          onChange={(e) =>
            setForm({ ...form, emergency_contact: e.target.value || undefined })
          }
        />
        <div className="sm:col-span-2">
          <Input
            label="Address"
            value={form.address || ''}
            onChange={(e) => setForm({ ...form, address: e.target.value || undefined })}
          />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" loading={loading}>
          {initial ? 'Update Employee' : 'Create Employee'}
        </Button>
      </div>
    </form>
  );
}
