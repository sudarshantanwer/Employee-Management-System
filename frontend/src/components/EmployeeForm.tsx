import { FormEvent, useEffect, useState } from 'react';
import { Employee, EmployeeFormData } from '../types';
import { Button, Input, Select } from './ui';

const DEPARTMENTS = ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales', 'Engineering'];

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
    department: 'IT',
    designation: '',
    salary: 0,
  });
  const [error, setError] = useState('');

  useEffect(() => {
    if (initial) {
      setForm({
        name: initial.name,
        email: initial.email,
        department: initial.department,
        designation: initial.designation,
        salary: initial.salary,
        manager_id: initial.manager_id || undefined,
      });
    }
  }, [initial]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (!form.name || !form.email || !form.designation || form.salary <= 0) {
      setError('Please fill in all required fields with valid values.');
      return;
    }
    try {
      await onSubmit(form);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save employee');
    }
  };

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
          options={DEPARTMENTS.map((d) => ({ value: d, label: d }))}
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
