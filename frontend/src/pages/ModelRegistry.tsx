import { DataState } from '@/components/ui/data-state';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { MotionCard } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Search, Download, GitCommit } from 'lucide-react';
import { ExperimentSummary } from '@/lib/mock-data';
import * as DashboardService from '@/features/dashboard/dashboard.service';

export function ModelRegistry() {
  const [models, setModels] = useState<ExperimentSummary[]>([]);

  const [search, setSearch] = useState('');

  useEffect(() => {
    async function load() {
      setModels(await DashboardService.getRecentExperiments());
    }
    load();
  }, []);

  const visible = models.filter(model => `${model.name} ${model.id}`.toLowerCase().includes(search.toLowerCase()));
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="max-w-7xl mx-auto space-y-8"
    >
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Model Registry</h1>
          <p className="text-muted-foreground mt-1">Versioned artifacts and deployment targets.</p>
        </div>
      </header>

      <div role="note" className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">Sample catalog · This view uses existing demonstration records, not live model artifacts.</div>
      <MotionCard className="p-0 overflow-hidden">
        <div className="p-4 border-b border-border flex flex-col sm:flex-row gap-4 items-center justify-between bg-muted/50">
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="search" aria-label="Search sample models" value={search} onChange={event => setSearch(event.target.value)}
              placeholder="Search models..."
              className="w-full pl-9 pr-4 py-2 bg-card border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            />
          </div>
        </div>

        {visible.length === 0 && <DataState title="No matching sample models" />}
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted text-muted-foreground font-medium border-b border-border">
              <tr>
                <th className="px-6 py-3">Version</th>
                <th className="px-6 py-3">Name</th>
                <th className="px-6 py-3">Tags</th>
                <th className="px-6 py-3">Accuracy</th>
                <th className="px-6 py-3">Params</th>
                <th className="px-6 py-3">Created</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {visible.map((model) => (
                <tr key={model.id} className="hover:bg-muted/50 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 font-medium text-foreground">
                      <GitCommit className="h-4 w-4 text-muted-foreground" />
                      {model.id}
                    </div>
                  </td>
                  <td className="px-6 py-4 font-medium text-foreground">{model.name}</td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      {model.tags.map(tag => (
                        <Badge key={tag} variant={
                          tag === 'production' ? 'success' :
                          tag === 'experimental' ? 'warning' : 'neutral'
                        } className="capitalize">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 font-medium text-foreground">{model.accuracy}</td>
                  <td className="px-6 py-4 text-muted-foreground">{model.parameters}</td>
                  <td className="px-6 py-4 text-muted-foreground">{model.date}</td>
                  <td className="px-6 py-4 text-right">
                    <button disabled aria-label="Model download unavailable" className="text-muted-foreground opacity-50 transition-opacity p-1 hover:bg-muted rounded" title="Artifact downloads are not connected">
                      <Download className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </MotionCard>
    </motion.div>
  );
}
