import { FormEvent, useEffect, useState } from 'react';
import { getErrorMessage } from '../api/client';
import { fetchProfile, updateProfile } from '../api/profile';
import { useAuth } from '../context/AuthContext';
import { Alert, Badge, Button, Card, Input, Spinner } from '../components/ui';
import { ProfileData } from '../types';

export function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [emergencyContact, setEmergencyContact] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadProfile = () => {
    setLoading(true);
    fetchProfile()
      .then((data) => {
        setProfile(data);
        if (data.employee) {
          setPhone(data.employee.phone || '');
          setAddress(data.employee.address || '');
          setEmergencyContact(data.employee.emergency_contact || '');
        }
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const updated = await updateProfile({
        phone: phone || undefined,
        address: address || undefined,
        emergency_contact: emergencyContact || undefined,
      });
      setProfile(updated);
      setSuccess('Profile updated successfully');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const formatSalary = (n: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);

  if (loading) return <Spinner />;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">My Profile</h1>
        <p className="text-sm text-slate-600">View and update your account information</p>
      </div>

      {error && <Alert message={error} />}
      {success && <Alert message={success} type="success" />}

      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Account</h2>
        <dl className="grid gap-3 sm:grid-cols-2">
          <div>
            <dt className="text-sm text-slate-500">Name</dt>
            <dd className="font-medium text-slate-900">{profile?.full_name || user?.full_name}</dd>
          </div>
          <div>
            <dt className="text-sm text-slate-500">Email</dt>
            <dd className="font-medium text-slate-900">{profile?.email}</dd>
          </div>
          <div>
            <dt className="text-sm text-slate-500">Role</dt>
            <dd>
              {profile && (
                <Badge color={profile.role === 'ADMIN' ? 'purple' : profile.role === 'MANAGER' ? 'blue' : 'green'}>
                  {profile.role}
                </Badge>
              )}
            </dd>
          </div>
        </dl>
      </Card>

      {profile?.employee ? (
        <>
          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Employee Record</h2>
            <dl className="grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-sm text-slate-500">Department</dt>
                <dd className="font-medium text-slate-900">{profile.employee.department}</dd>
              </div>
              <div>
                <dt className="text-sm text-slate-500">Designation</dt>
                <dd className="font-medium text-slate-900">{profile.employee.designation}</dd>
              </div>
              <div>
                <dt className="text-sm text-slate-500">Salary</dt>
                <dd className="font-medium text-slate-900">{formatSalary(profile.employee.salary)}</dd>
              </div>
            </dl>
          </Card>

          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Contact Information</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input label="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
              <Input label="Address" value={address} onChange={(e) => setAddress(e.target.value)} />
              <Input
                label="Emergency Contact"
                value={emergencyContact}
                onChange={(e) => setEmergencyContact(e.target.value)}
              />
              <Button type="submit" loading={saving}>
                Save Changes
              </Button>
            </form>
          </Card>
        </>
      ) : (
        <Card className="p-6">
          <p className="text-sm text-slate-600">
            No employee profile is linked to your account. Contact an administrator to link your
            employee record.
          </p>
        </Card>
      )}
    </div>
  );
}
