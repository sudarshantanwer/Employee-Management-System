import { FormEvent, useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { getErrorMessage } from '../api/client';
import { GoogleSetupHelp, isGoogleOriginError } from '../components/GoogleSetupHelp';
import { GoogleSignInButton, isGoogleAuthConfigured } from '../components/GoogleSignInButton';
import { useAuth } from '../context/AuthContext';
import { Alert, Button, Input } from '../components/ui';

export function LoginPage() {
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const showGoogle = isGoogleAuthConfigured();

  useEffect(() => {
    const urlError = searchParams.get('error');
    if (urlError) {
      setError(decodeURIComponent(urlError));
    }
  }, [searchParams]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
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
          <h1 className="text-2xl font-bold text-white">Welcome back</h1>
          <p className="mt-2 text-slate-300">Sign in to Employee Management System</p>
        </div>
        <div className="rounded-2xl bg-white p-8 shadow-2xl">
          {error && (
            <div className="mb-4">
              <Alert message={error} />
            </div>
          )}

          {error && isGoogleOriginError(error) && (
            <div className="mb-4">
              <GoogleSetupHelp compact />
            </div>
          )}

          {showGoogle && (
            <>
              <GoogleSignInButton loading={isLoading} text="signin_with" />
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="bg-white px-3 text-slate-500">or continue with email</span>
                </div>
              </div>
            </>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
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
              placeholder="••••••••"
              required
            />
            <Button type="submit" className="w-full" loading={isLoading}>
              Sign in with email
            </Button>
          </form>
          <p className="mt-6 text-center text-sm text-slate-600">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-brand-600 hover:text-brand-700">
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
