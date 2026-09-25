import { Cpu, Network, Box, ArrowRight } from 'lucide-react';

/** An architecture guide, not an indication of an active training stage. */
export function FederationFlow() {
  const stages = [
    { icon: Cpu, title: 'Local training', description: 'Learning at the edge' },
    { icon: Network, title: 'Model aggregation', description: 'Combining client updates' },
    { icon: Box, title: 'Global model', description: 'Shared anomaly detection' },
  ];
  return <section aria-label="Federated learning architecture" className="rounded-xl border border-border bg-card px-5 py-4">
    <p className="eyebrow mb-4">How the federation works · Architecture guide</p>
    <ol className="grid gap-4 sm:grid-cols-3">
      {stages.map(({ icon: Icon, title, description }, index) => <li key={title} className="flex min-w-0 items-center gap-3">
        <span className="rounded-lg bg-primary/10 p-2 text-primary"><Icon size={19} aria-hidden="true" /></span>
        <div className="min-w-0"><p className="text-sm font-medium">{title}</p><p className="text-xs text-muted-foreground">{description}</p></div>
        {index < 2 && <ArrowRight size={16} className="ml-auto hidden shrink-0 text-muted-foreground sm:block" aria-hidden="true" />}
      </li>)}
    </ol>
  </section>;
}
