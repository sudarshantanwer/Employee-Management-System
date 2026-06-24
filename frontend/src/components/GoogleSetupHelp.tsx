interface GoogleSetupHelpProps {
  compact?: boolean;
  errorType?: 'redirect' | 'origin' | 'general';
}

const REDIRECT_URI = 'http://localhost:8000/api/v1/auth/google/callback';

export function GoogleSetupHelp({ compact = false, errorType = 'redirect' }: GoogleSetupHelpProps) {
  if (compact || errorType === 'redirect') {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-3 text-xs text-amber-900">
        <p className="font-semibold">
          {errorType === 'redirect'
            ? 'Fix: Error 400 redirect_uri_mismatch'
            : 'Google OAuth one-time setup'}
        </p>
        <p className="mt-2">
          1. Open{' '}
          <a
            href="https://console.cloud.google.com/apis/credentials"
            target="_blank"
            rel="noreferrer"
            className="font-medium underline"
          >
            Google Cloud Console → Credentials
          </a>
        </p>
        <p className="mt-1">2. Click your OAuth 2.0 Client ID (type: Web application)</p>
        <p className="mt-1">
          3. Under <strong>Authorized redirect URIs</strong>, click <strong>Add URI</strong> and
          paste this <em>exactly</em> (no trailing slash):
        </p>
        <div className="mt-2 rounded border border-amber-300 bg-white px-2 py-2 font-mono text-[11px] break-all select-all">
          {REDIRECT_URI}
        </div>
        <p className="mt-2">4. Click <strong>Save</strong>, wait 1–2 minutes, then try again.</p>
        <p className="mt-1 text-amber-800">
          Also add your Gmail as a <strong>Test user</strong> on the OAuth consent screen.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      <p className="font-semibold">Google Sign-In setup</p>
      <p className="mt-2">
        Add this redirect URI in Google Cloud Console:
      </p>
      <p className="mt-1 break-all font-mono text-xs">{REDIRECT_URI}</p>
    </div>
  );
}

export function isGoogleOriginError(message: string): boolean {
  const lower = message.toLowerCase();
  return (
    lower.includes('origin') ||
    lower.includes('invalid_client') ||
    lower.includes('401') ||
    lower.includes('400') ||
    lower.includes('blocked') ||
    lower.includes('redirect') ||
    lower.includes('mismatch') ||
    lower.includes('authorized')
  );
}

export function getGoogleRedirectUri(): string {
  return REDIRECT_URI;
}
