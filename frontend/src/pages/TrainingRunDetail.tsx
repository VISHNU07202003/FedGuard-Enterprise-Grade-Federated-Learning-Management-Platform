import { DataState } from '@/components/ui/data-state';
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MotionCard } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft } from 'lucide-react';

export function TrainingRunDetail() {
  const { id } = useParams();
  const [run, setRun] = useState<any>(null);
  const [rounds, setRounds] = useState<any[]>([]);
  const [privacy, setPrivacy] = useState<any>(null);
  const [edge, setEdge] = useState<any>(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [partial, setPartial] = useState(false);

  useEffect(() => {
    async function fetchDetails() {
      setLoading(true);
      setFailed(false);
      setPartial(false);
      setRun(null);
      setRounds([]);
      setPrivacy(null);
      setEdge(null);
      try {
        const token = localStorage.getItem('token');
        const headers: HeadersInit = token ? { Authorization: `Bearer ${token}` } : {};
        const [runRes, roundsRes, privacyRes, edgeRes] = await Promise.all([
          fetch(`${API_URL}/api/v1/training/runs/${id}`, { headers }),
          fetch(`${API_URL}/api/v1/training/runs/${id}/rounds`, { headers }),
          fetch(`${API_URL}/api/v1/training/runs/${id}/privacy`, { headers }),
          fetch(`${API_URL}/api/v1/training/runs/${id}/edge`, { headers })
        ]);
        if (!runRes.ok) setFailed(true);
        setPartial(!roundsRes.ok || !privacyRes.ok || !edgeRes.ok);
        if (runRes.ok) setRun(await runRes.json());
        if (roundsRes.ok) setRounds(await roundsRes.json());
        if (privacyRes.ok) setPrivacy(await privacyRes.json());
        if (edgeRes.ok) setEdge(await edgeRes.json());
      } catch (err) {
        console.error(err);
        setFailed(true);
      } finally {
        setLoading(false);
      }
    }
    fetchDetails();
  }, [id, API_URL]);

  if (loading) return <DataState kind="loading" title="Loading training details" />;
  if (failed || !run) return <DataState kind="error" title="Training details unavailable" description="The run could not be retrieved. Check your connection or return to Training runs." />;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-7xl mx-auto space-y-8">
      <Link to="/training" className="inline-flex items-center text-sm text-blue-500 hover:underline">
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to Training Runs
      </Link>

      <header>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">{run.run_id}</h1>
        <div className="flex gap-4 mt-2">
          <Badge variant={run.status === 'completed' ? 'success' : 'secondary'} className="capitalize">
            {run.status}
          </Badge>
          <span className="text-sm text-muted-foreground">{run.model_type} • {run.strategy}</span>
        </div>
      </header>

      {partial && <DataState kind="error" title="Some run details are unavailable" description="Round, privacy, or edge information could not be loaded. The available data is shown below." />}
      {privacy && privacy.enabled && (
        <MotionCard className="p-6 bg-slate-900 border-indigo-900 text-slate-100">
          <div className="flex flex-wrap gap-3 items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-indigo-400">Privacy Preserving Training Enabled</h3>
            <Badge className="bg-indigo-600 hover:bg-indigo-500">DP Mode: {privacy.dp_mode}</Badge>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
            <div>
              <div className="text-muted-foreground mb-1">Epsilon Spent</div>
              <div className="font-medium text-lg">{privacy.epsilon_spent != null ? privacy.epsilon_spent.toFixed(4) : 'N/A'}</div>
            </div>
            <div>
              <div className="text-muted-foreground mb-1">Target Epsilon</div>
              <div className="font-medium text-lg">{privacy.target_epsilon ?? 'N/A'}</div>
            </div>
            <div>
              <div className="text-muted-foreground mb-1">Noise Multiplier</div>
              <div className="font-medium text-lg">{privacy.noise_multiplier != null ? privacy.noise_multiplier.toFixed(4) : 'N/A'}</div>
            </div>
            <div>
              <div className="text-muted-foreground mb-1">Max Grad Norm</div>
              <div className="font-medium text-lg">{privacy.max_grad_norm ?? 'N/A'}</div>
            </div>
          </div>
        </MotionCard>
      )}

      {edge && edge.enabled && (
        <MotionCard className="p-6 bg-slate-900 border-teal-900 text-slate-100">
          <div className="flex flex-wrap gap-3 items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-teal-400">Edge Device Simulation</h3>
            <Badge className="bg-teal-600 hover:bg-teal-500">Enabled</Badge>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 text-sm">
            <div>
              <div className="text-muted-foreground mb-1">Edge Devices</div>
              <div className="font-medium text-lg">{edge.active_clients || 0}</div>
            </div>
            <div>
              <div className="text-muted-foreground mb-1">Avg Latency</div>
              <div className="font-medium text-lg">{edge.avg_latency_ms ?? 'Unavailable'} ms</div>
            </div>
            <div>
              <div className="text-muted-foreground mb-1">Availability</div>
              <div className="font-medium text-lg">{edge.availability_rate != null ? `${(edge.availability_rate * 100).toFixed(1)}%` : 'Unavailable'}</div>
            </div>
            <div>
              <div className="text-muted-foreground mb-1">Battery Skipped</div>
              <div className="font-medium text-lg text-amber-400">{edge.battery_limited_clients || 0}</div>
            </div>
            <div>
              <div className="text-muted-foreground mb-1">Edge Stragglers</div>
              <div className="font-medium text-lg text-red-400">{edge.edge_stragglers || 0}</div>
            </div>
          </div>
        </MotionCard>
      )}

      <MotionCard className="p-6">
        <h3 className="text-lg font-semibold mb-4">Round Details & Reliability</h3>
        {!rounds.length && <DataState title="No round records available" />}
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted text-muted-foreground font-medium border-b border-border">
              <tr>
                <th className="px-4 py-3">Round</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Clients Completed</th>
                <th className="px-4 py-3">Stragglers</th>
                <th className="px-4 py-3">Rejections</th>
                <th className="px-4 py-3">Dropouts</th>
                <th className="px-4 py-3">Loss</th>
                <th className="px-4 py-3">F1 Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {rounds.map((r) => (
                <tr key={r.round_number} className="hover:bg-muted/50">
                  <td className="px-4 py-3 font-medium">{r.round_number}</td>
                  <td className="px-4 py-3">
                    <Badge variant={r.round_status === 'failed' ? 'destructive' : r.round_status === 'partial_success' ? 'warning' : 'success'}>
                      {r.round_status?.replace('_', ' ')}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">{r.clients_completed} / {r.clients_selected}</td>
                  <td className="px-4 py-3 text-blue-300 font-medium">{r.straggler_count > 0 ? r.straggler_count : '-'}</td>
                  <td className="px-4 py-3 text-amber-300 font-medium">{r.clients_rejected > 0 ? r.clients_rejected : '-'}</td>
                  <td className="px-4 py-3">{r.clients_timed_out + r.clients_failed}</td>
                  <td className="px-4 py-3 text-muted-foreground">{r.val_loss?.toFixed(4) || '-'}</td>
                  <td className="px-4 py-3 text-muted-foreground">{r.global_f1?.toFixed(4) || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </MotionCard>
    </motion.div>
  );
}
