import { DataState } from '@/components/ui/data-state';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { MotionCard } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MotionButton } from '@/components/ui/button';
import { Search, ArrowRight } from 'lucide-react';

export function TrainingRuns() {
  const [runs, setRuns] = useState<any[]>([]);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const USE_MOCK = import.meta.env.VITE_USE_MOCK_DATA === 'true';

  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    async function load() {
      if (USE_MOCK) {
        setLoading(false); // Existing mock mode has no run records.
        return;
      }
      try {
        const token = localStorage.getItem('token');
        const headers: HeadersInit = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await fetch(`${API_URL}/api/v1/training/runs`, { headers });
        if (response.ok) {
          const data = await response.json();
          setRuns(data);
        } else {
          setFailed(true);
        }
      } catch (error) {
        console.error("Failed to load runs", error);
        setFailed(true);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [API_URL, USE_MOCK]);

  const visible = runs.filter(run => run.run_id.toLowerCase().includes(search.toLowerCase()) && (statusFilter === 'all' || run.status === statusFilter));

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="max-w-7xl mx-auto space-y-8"
    >
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Training Runs</h1>
          <p className="text-muted-foreground mt-1">Federated learning aggregation sessions.</p>
        </div>
        <MotionButton disabled title="Starting training is not available in this interface">
          New Training Run
        </MotionButton>
      </header>

      <MotionCard className="p-0 overflow-hidden">
        <div className="p-4 border-b border-border flex flex-col sm:flex-row gap-4 items-center justify-between bg-muted/50">
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="search" aria-label="Search training runs" value={search} onChange={event => setSearch(event.target.value)}
              placeholder="Search runs..."
              className="w-full pl-9 pr-4 py-2 bg-card border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            />
          </div>
          <select aria-label="Filter training runs by status" className="table-filter w-full sm:w-auto" value={statusFilter} onChange={event => setStatusFilter(event.target.value)}>
            <option value="all">All statuses</option>
            { ['running', 'completed', 'failed', 'pending'].map(status => <option key={status} value={status}>{status}</option>) }
          </select>
        </div>

        {loading ? <DataState kind="loading" title="Loading training runs" /> : failed ? <DataState kind="error" title="Could not load training runs" description="Check your connection and refresh to try again." /> : visible.length === 0 ? <DataState title="No training runs found" description="No records match this view. Try clearing your filters." /> : <div className="overflow-x-auto">
          <table aria-label="Training runs" className="w-full text-sm text-left">
            <thead className="bg-muted text-muted-foreground font-medium border-b border-border">
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
              {visible.map((run) => (
                <tr key={run.id} className="hover:bg-muted/50 transition-colors group">
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
                    <button aria-label={`View run ${run.run_id}`} onClick={() => window.location.href=`/training/${run.run_id}`} className="text-primary transition-opacity p-1 hover:bg-muted rounded">
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>}
      </MotionCard>
    </motion.div>
  );
}
