import { FormEvent, useState } from 'react';
import { Link } from 'react-router-dom';
import { getErrorMessage } from '../api/client';
import { forgotPassword } from '../api/auth';
import { Alert, Button, Input } from '../components/ui';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-brand-900 to-slate-900 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
        <h1 className="text-2xl font-bold text-slate-900">Forgot Password</h1>
        <p className="mt-2 text-sm text-slate-600">
          Enter your email and we'll send a reset link if an account exists.
        </p>

        {error && <div className="mt-4"><Alert message={error} /></div>}
        {sent ? (
          <div className="mt-6 space-y-4">
            <Alert message="If an account exists with that email, a reset link has been sent. Check the server logs in development." type="success" />
            <Link to="/login" className="block text-center text-sm font-medium text-brand-600 hover:text-brand-700">
              Back to login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <Button type="submit" className="w-full" loading={loading}>Send Reset Link</Button>
            <p className="text-center text-sm text-slate-600">
              <Link to="/login" className="font-medium text-brand-600 hover:text-brand-700">Back to login</Link>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
