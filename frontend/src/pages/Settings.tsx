import { MotionCard } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/features/auth/AuthContext';
import { User, ShieldCheck } from 'lucide-react';

export function Settings() {
  const { user } = useAuth();
  return <div className="max-w-5xl mx-auto space-y-8">
    <header><p className="eyebrow mb-2 text-primary">Workspace / Account</p><h1 className="text-3xl font-semibold tracking-tight">Settings</h1><p className="mt-2 text-muted-foreground">Your identity and workspace access.</p></header>
    <div className="grid gap-6 md:grid-cols-2">
      <MotionCard className="p-6"><User className="mb-5 text-primary" size={24} /><h2 className="text-lg font-semibold">Account profile</h2>
        <dl className="mt-6 space-y-5 text-sm">
          <div><dt className="text-muted-foreground">Full name</dt><dd className="mt-1">{user?.full_name || 'Not provided'}</dd></div>
          <div><dt className="text-muted-foreground">Email address</dt><dd className="mt-1 break-all">{user?.email || 'Not available'}</dd></div>
          <div><dt className="mb-2 text-muted-foreground">Assigned role</dt><dd><Badge variant="outline" className="capitalize">{user?.role || 'Not available'}</Badge></dd></div>
        </dl>
      </MotionCard>
      <MotionCard className="p-6"><ShieldCheck className="mb-5 text-primary" size={24} /><h2 className="text-lg font-semibold">Managed access</h2><p className="mt-4 text-sm leading-relaxed text-muted-foreground">Your assigned role determines access to workspace features. Contact your administrator for account or permission changes.</p><p className="mt-5 border-t border-border pt-5 text-sm text-muted-foreground">Profile editing, notification preferences, and infrastructure settings are not available in this interface.</p></MotionCard>
    </div>
  </div>;
}
