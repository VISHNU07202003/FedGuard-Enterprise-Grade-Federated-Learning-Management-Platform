import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { ShieldCheck, Network, ArrowRight, LockKeyhole } from 'lucide-react';
import { useAuth } from '../features/auth/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('admin@fedguard.dev');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post('/api/v1/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      login(response.data.access_token);
      navigate(from, { replace: true });
    } catch (err: unknown) {
      console.error('Sign-in failed', axios.isAxiosError(err) ? err.response?.status || err.code : 'Unexpected error');
      setError(axios.isAxiosError(err) && err.response?.status === 401 ? 'The email or password was not recognized. Please try again.' : 'Unable to sign in. Check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="login-surface min-h-dvh flex items-center justify-center px-5 py-10 sm:px-10">
      <div className="grid w-full max-w-6xl items-center gap-12 lg:grid-cols-[1.2fr_1fr] lg:gap-24">
        <section>
          <div className="mb-10 flex items-center gap-3"><ShieldCheck className="text-primary" size={32} /><span className="text-xl font-semibold tracking-tight">FedGuard</span></div>
          <p className="eyebrow mb-5 text-primary">Distributed Intelligence. Private by Design.</p>
          <h1 className="text-4xl sm:text-5xl xl:text-6xl font-semibold tracking-tight leading-[1.1]">Intelligence at the edge.<br /><span className="text-primary">Privacy at the core.</span></h1>
          <p className="mt-6 max-w-lg text-lg leading-relaxed text-muted-foreground">Privacy-preserving federated anomaly detection. Train together, detect threats, and keep sensitive data where it belongs.</p>
          <div className="mt-10 hidden sm:flex items-center gap-4 border-t border-border pt-6 text-sm text-muted-foreground"><Network size={20} className="text-primary" /><span>Edge clients<span className="mx-3 text-primary">/</span>Model updates<span className="mx-3 text-primary">/</span>Global learning</span></div>
        </section>
        <section className="rounded-2xl border border-border bg-card p-6 sm:p-9 shadow-2xl shadow-black/20" aria-labelledby="sign-in-title">
          <LockKeyhole className="mb-6 text-primary" size={24} />
          <h2 id="sign-in-title" className="text-2xl font-semibold tracking-tight">Welcome to your workspace</h2>
          <p className="mt-2 mb-8 text-sm text-muted-foreground">Sign in with your FedGuard account to continue.</p>
          <form className="space-y-5" onSubmit={handleSubmit} aria-busy={isLoading}>
            {error && <div id="login-error" role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>}
            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium">Email address</label>
              <input id="email" name="email" type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} aria-describedby={error ? 'login-error' : undefined} className="w-full rounded-lg border border-input px-3 py-3 text-sm" />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-medium">Password</label>
              <input id="password" name="password" type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} aria-describedby={error ? 'login-error' : undefined} className="w-full rounded-lg border border-input px-3 py-3 text-sm" />
            </div>
            <button type="submit" disabled={isLoading} className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-60">{isLoading ? 'Signing in…' : 'Sign in to FedGuard'}<ArrowRight size={16} /></button>
          </form>
          <p className="mt-6 border-t border-border pt-5 text-xs leading-relaxed text-muted-foreground">Access is managed by your workspace administrator.</p>
        </section>
      </div>
    </main>
  );
}
