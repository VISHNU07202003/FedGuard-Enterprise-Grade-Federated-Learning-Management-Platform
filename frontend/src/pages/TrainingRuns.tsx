import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { MotionCard } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MotionButton } from '@/components/ui/button';
import { Search, Filter, ArrowRight } from 'lucide-react';

export function TrainingRuns() {
  const [runs, setRuns] = useState<any[]>([]);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const USE_MOCK = import.meta.env.VITE_USE_MOCK_DATA === 'true';

  useEffect(() => {
    async function load() {
      if (USE_MOCK) {
        // mock logic fallback omitted for brevity
        return;
      }
      try {
        const response = await fetch(`${API_URL}/api/v1/training/runs`);
        if (response.ok) {
          const data = await response.json();
          setRuns(data);
        }
      } catch (error) {
        console.error("Failed to load runs", error);
      }
    }
    load();
  }, [API_URL, USE_MOCK]);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-8 max-w-7xl mx-auto space-y-8"
    >
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Training Runs</h1>
          <p className="text-muted-foreground mt-1">Federated learning aggregation sessions.</p>
        </div>
        <MotionButton>
          New Training Run
        </MotionButton>
      </header>

      <MotionCard className="p-0 overflow-hidden">
        <div className="p-4 border-b border-border flex flex-col sm:flex-row gap-4 items-center justify-between bg-slate-50/50">
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search runs..." 
              className="w-full pl-9 pr-4 py-2 bg-white border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            />
          </div>
          <MotionButton variant="outline" size="sm" className="w-full sm:w-auto gap-2">
            <Filter className="h-4 w-4" />
            Filter
          </MotionButton>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-muted-foreground font-medium border-b border-border">
              <tr>
                <th className="px-6 py-3">Run ID</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Privacy</th>
                <th className="px-6 py-3">Model</th>
                <th className="px-6 py-3">Strategy</th>
                <th className="px-6 py-3">MLflow</th>
                <th className="px-6 py-3">Started</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {runs.map((run) => (
                <tr key={run.id} className="hover:bg-slate-50/50 transition-colors group">
                  <td className="px-6 py-4 font-medium text-foreground">{run.run_id}</td>
                  <td className="px-6 py-4">
                    <Badge variant={
                      run.status === 'completed' ? 'success' : 
                      run.status === 'running' ? 'warning' : 'secondary'
                    } className="capitalize">
                      {run.status}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    {run.privacy_enabled ? (
                      <Badge className="bg-indigo-600 hover:bg-indigo-500">DP: {run.dp_mode}</Badge>
                    ) : (
                      <span className="text-muted-foreground text-xs">None</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-muted-foreground">{run.model_type}</td>
                  <td className="px-6 py-4 text-muted-foreground">{run.strategy}</td>
                  <td className="px-6 py-4 text-muted-foreground">
                    {run.mlflow_run_id ? (
                      <span className="text-blue-500 font-mono text-xs" title={`Experiment: ${run.mlflow_experiment_id}`}>
                        {run.mlflow_run_id.substring(0, 8)}...
                      </span>
                    ) : (
                      <span className="text-slate-300">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-muted-foreground">{new Date(run.started_at).toLocaleString()}</td>
                  <td className="px-6 py-4 text-right">
                    <button onClick={() => window.location.href=`/training/${run.run_id}`} className="text-primary opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-slate-100 rounded">
                      <ArrowRight className="h-4 w-4" />
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
