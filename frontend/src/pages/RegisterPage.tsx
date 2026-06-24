import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getErrorMessage } from '../api/client';
import { GoogleSignInButton, isGoogleAuthConfigured } from '../components/GoogleSignInButton';
import { useAuth } from '../context/AuthContext';
import { Alert, Button, Input } from '../components/ui';

export function RegisterPage() {
  const { register, isLoading } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const showGoogle = isGoogleAuthConfigured();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    try {
      await register(email, password, fullName);
      navigate('/dashboard');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-brand-900 to-slate-900 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-500 text-xl font-bold text-white shadow-lg">
            EMS
          </div>
          <h1 className="text-2xl font-bold text-white">Create account</h1>
          <p className="mt-2 text-slate-300">Register as an employee</p>
        </div>
        <div className="rounded-2xl bg-white p-8 shadow-2xl">
          {error && (
            <div className="mb-4">
              <Alert message={error} />
            </div>
          )}

          {showGoogle && (
            <>
              <GoogleSignInButton loading={isLoading} text="signup_with" />
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="bg-white px-3 text-slate-500">or register with email</span>
                </div>
              </div>
            </>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="John Doe"
              required
            />
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min. 8 characters"
              required
            />
            <Button type="submit" className="w-full" loading={isLoading}>
              Create account with email
            </Button>
          </form>
          <p className="mt-6 text-center text-sm text-slate-600">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-brand-600 hover:text-brand-700">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
