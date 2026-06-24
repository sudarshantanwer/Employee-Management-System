import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { setStoredTokens, setStoredUser } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Spinner } from '../components/ui';

export function GoogleCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [message, setMessage] = useState('Completing Google sign-in...');

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
      return;
    }

    const error = searchParams.get('error');
    if (error) {
      navigate(`/login?error=${encodeURIComponent(error)}`, { replace: true });
      return;
    }

    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    const userId = searchParams.get('user_id');
    const email = searchParams.get('email');
    const fullName = searchParams.get('full_name');
    const role = searchParams.get('role');

    if (!accessToken || !refreshToken || !userId || !email || !role) {
      setMessage('Invalid Google callback. Redirecting to login...');
      setTimeout(() => navigate('/login', { replace: true }), 1500);
      return;
    }

    setStoredTokens({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer',
    });
    setStoredUser({
      user_id: userId,
      email,
      full_name: fullName || email,
      role,
    });

    window.location.href = '/dashboard';
  }, [searchParams, navigate, isAuthenticated]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="text-center">
        <Spinner />
        <p className="mt-4 text-sm text-slate-600">{message}</p>
      </div>
    </div>
  );
}
