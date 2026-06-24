import { FormEvent, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { getErrorMessage } from '../api/client';
import { resetPassword } from '../api/auth';
import { Alert, Button, Input } from '../components/ui';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [token, setToken] = useState(searchParams.get('token') || '');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await resetPassword(token, password);
      navigate('/login');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-brand-900 to-slate-900 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
        <h1 className="text-2xl font-bold text-slate-900">Reset Password</h1>
        <p className="mt-2 text-sm text-slate-600">Enter your reset token and new password.</p>

        {error && <div className="mt-4"><Alert message={error} /></div>}

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <Input label="Reset Token" value={token} onChange={(e) => setToken(e.target.value)} required />
          <Input label="New Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Input label="Confirm Password" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
          <Button type="submit" className="w-full" loading={loading}>Reset Password</Button>
          <p className="text-center text-sm text-slate-600">
            <Link to="/login" className="font-medium text-brand-600 hover:text-brand-700">Back to login</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
