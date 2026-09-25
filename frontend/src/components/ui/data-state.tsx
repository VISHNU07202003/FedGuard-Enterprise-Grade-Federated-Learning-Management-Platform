import { AlertCircle, Database, Loader2 } from 'lucide-react';

export function DataState({ kind = 'empty', title, description }: { kind?: 'loading' | 'error' | 'empty'; title: string; description?: string }) {
  const Icon = kind === 'loading' ? Loader2 : kind === 'error' ? AlertCircle : Database;
  return <div role={kind === 'error' ? 'alert' : 'status'} className="data-state">
    <Icon size={24} aria-hidden="true" className={kind === 'loading' ? 'animate-spin text-primary' : kind === 'error' ? 'text-amber-400' : 'text-muted-foreground'} />
    <p className="font-medium text-foreground">{title}</p>
    {description && <p className="max-w-md text-sm text-muted-foreground">{description}</p>}
  </div>;
}
