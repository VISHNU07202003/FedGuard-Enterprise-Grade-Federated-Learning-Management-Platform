import { DataState } from '@/components/ui/data-state';
import { FederationFlow } from '@/components/federation-flow';
import { motion } from 'framer-motion';
import { MotionCard } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ChartCard, PerformanceLineChart, AnomalyAreaChart } from '@/components/ui/charts';
import { useDashboardSummary } from '@/hooks/useDashboard';
import { useTrainingWebSocket } from '@/hooks/useTrainingWebSocket';
import { ShieldAlert, GitCommit, CheckCircle2, XCircle, AlertCircle, HelpCircle, Cpu, Zap } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } }
};

export function Dashboard() {
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useDashboardSummary();

  // Connect WS if there's a running job
  const runId = data?.current_training_run?.run_id || null;
  const { status: wsStatus, latestEvent } = useTrainingWebSocket(runId);

  const [liveRound, setLiveRound] = useState(0);
  const [liveStatus, setLiveStatus] = useState<string>('');

  useEffect(() => {
    if (latestEvent) {
      if (latestEvent.event === 'round.started') setLiveRound(latestEvent.round || 0);
      if (latestEvent.event.startsWith('training.')) setLiveStatus(latestEvent.payload?.status || '');

      if (latestEvent.event === 'training.completed') {
        // Refetch everything when done
        queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
      }
    }
  }, [latestEvent, queryClient]);

  if (isLoading) return <DataState kind="loading" title="Loading federation overview" description="Retrieving training, client health, and model metrics." />;
  if (isError) return <DataState kind="error" title="Overview unavailable" description="We could not retrieve the latest data. Check your connection and refresh to try again." />;
  if (!data) return <DataState title="No overview data available" />;

  const {
    kpi_metrics,
    current_training_run,
    client_health_summary,
    model_performance_series: rounds,
    anomalies,
    recent_security_events: securityEvents,
    recent_experiments: experiments,
    service_health: systemStatus
  } = data;

  return (
    <motion.div
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {/* 1. Page Header */}
      <motion.div variants={itemVariants} className="flex flex-wrap gap-4 justify-between items-center">
        <div>
          <p className="eyebrow mb-2 text-primary">Federation / Operations</p><h1 className="text-3xl font-semibold tracking-tight text-foreground">Federation overview</h1>
          <p className="text-muted-foreground mt-1">Training progress, distributed clients, and anomaly intelligence in one workspace.</p>
        </div>
        <div className="flex items-center gap-2">
           {wsStatus === 'connecting' && <Badge variant="outline">Connecting…</Badge>}
           {!runId && <Badge variant="secondary">No active stream</Badge>}
           {wsStatus === 'connected' && <Badge variant="outline" className="text-green-300 border-green-500/30 bg-green-500/10"><span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"></span>Live</Badge>}
           {wsStatus === 'reconnecting' && <Badge variant="outline" className="text-amber-300 border-amber-500/30 bg-amber-500/10">Reconnecting...</Badge>}
           {(wsStatus === 'disconnected' || wsStatus === 'error') && runId && <Badge variant="outline" className="text-muted-foreground">Offline</Badge>}
        </div>
      </motion.div>

      {/* 2. KPI Cards */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MotionCard className="p-5 metric-card">
          <h3 className="text-sm font-medium text-muted-foreground">Total Clients</h3>
          <p className="text-3xl font-bold mt-2">{kpi_metrics.total_clients}</p>
        </MotionCard>
        <MotionCard className="p-5 metric-card">
          <h3 className="text-sm font-medium text-muted-foreground">Active Runs</h3>
          <p className="text-3xl font-bold mt-2">{kpi_metrics.active_training_runs}</p>
        </MotionCard>
        <MotionCard className="p-5 metric-card">
          <h3 className="text-sm font-medium text-muted-foreground">Anomalies (24h)</h3>
          <p className="text-3xl font-bold mt-2">{kpi_metrics.anomalies_detected_24h}</p>
        </MotionCard>
        <MotionCard className="p-5 metric-card">
          <h3 className="text-sm font-medium text-muted-foreground">System Score</h3>
          <p className="text-3xl font-bold mt-2">{kpi_metrics.system_health_score}/100</p>
        </MotionCard>
      </motion.div>

      {/* 3. Training Run & Client Health */}
      <FederationFlow />
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <MotionCard className="p-6 lg:col-span-2 min-w-0">
          <div className="flex flex-wrap gap-3 justify-between items-start mb-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground">Current Training Run</h3>
              <p className="text-sm text-muted-foreground break-all">run-id: {current_training_run?.run_id || 'None'}</p>

              <div className="mt-2 flex flex-col gap-2">
                {current_training_run?.mlflow_run_id && (
                  <div className="flex items-center">
                    <Badge variant="outline" className="text-blue-300 border-blue-500/30 bg-blue-500/10">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mr-1.5"></span>
                      MLflow Tracked
                    </Badge>
                    {current_training_run.mlflow_tracking_uri?.startsWith('http') && (
                      <a href={`${current_training_run.mlflow_tracking_uri}/#/experiments/${current_training_run.mlflow_experiment_id}/runs/${current_training_run.mlflow_run_id}`}
                         target="_blank" rel="noreferrer"
                         className="ml-2 text-xs text-blue-500 hover:underline">
                        View in MLflow
                      </a>
                    )}
                    {current_training_run.mlflow_tracking_uri?.startsWith('file') && (
                      <span className="ml-2 text-xs text-muted-foreground" title={`Local tracking: ${current_training_run.mlflow_tracking_uri}`}>(Local File tracking)</span>
                    )}
                  </div>
                )}

                {current_training_run?.privacy_enabled && (
                  <div className="flex items-center">
                    <Badge className="bg-indigo-600 hover:bg-indigo-500">
                      Privacy Preserving: {current_training_run.dp_mode}
                    </Badge>
                  </div>
                )}
              </div>
            </div>
            <Badge variant={(liveStatus || current_training_run?.status) === 'running' ? 'success' : 'secondary'}>
              {liveStatus || current_training_run?.status || 'Idle'}
            </Badge>
          </div>
          {current_training_run ? <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="font-medium text-foreground">
                Round {Math.max(liveRound, current_training_run?.current_round || 0)} of {current_training_run?.total_rounds || 0}
              </span>
              <span className="text-muted-foreground">
                {current_training_run?.total_rounds > 0 ? Math.round((Math.max(liveRound, current_training_run.current_round) / current_training_run.total_rounds) * 100) : 0}% Complete
              </span>
            </div>
            <Progress aria-label="Training round progress" value={current_training_run?.total_rounds > 0 ? (Math.max(liveRound, current_training_run.current_round) / current_training_run.total_rounds) * 100 : 0} className="h-2" />
          </div> : <DataState title="No training run reported" description="Run progress will appear here when a training run is available." />}
        </MotionCard>

        <MotionCard className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Reliability & Client Health</h3>

          <div className="mb-4 p-3 bg-muted border border-border rounded-lg space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Round Status</span>
              <Badge variant={liveStatus === 'running' ? 'success' : 'secondary'} className="capitalize">{liveStatus || current_training_run?.status || 'Idle'}</Badge>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Training clients</span>
              <span className="font-medium text-foreground">{client_health_summary.training}</span>
            </div>

          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm"><span className="text-amber-300">Unhealthy</span><span className="font-medium">{client_health_summary.error}</span></div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-foreground">
                <span className="w-2.5 h-2.5 rounded-full bg-green-500" /> Online
              </div>
              <span className="font-medium">{client_health_summary.online}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-foreground">
                <span className="w-2.5 h-2.5 rounded-full bg-slate-300" /> Offline
              </div>
              <span className="font-medium">{client_health_summary.offline}</span>
            </div>
          </div>
        </MotionCard>
      </motion.div>

      {/* Edge Device Simulation (Optional) */}
      {data.edge_simulation?.enabled && (
        <motion.div variants={itemVariants}>
          <MotionCard className="p-6 bg-slate-900 border-blue-900 text-slate-100 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-32 opacity-10 pointer-events-none">
              <Cpu className="w-64 h-64 text-blue-500" />
            </div>
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-blue-400 flex items-center gap-2">
                  <Zap className="w-5 h-5" /> Edge Device Simulation
                </h3>
                <Badge className="bg-blue-600 hover:bg-blue-500 text-white">Active</Badge>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 text-sm">
                <div>
                  <div className="text-muted-foreground mb-1">Active Edge Clients</div>
                  <div className="font-medium text-lg">{data.edge_simulation.active_edge_clients || 0}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">Average Latency</div>
                  <div className="font-medium text-lg">{data.edge_simulation.average_latency_ms ?? 'Unavailable'} ms</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">Availability Rate</div>
                  <div className="font-medium text-lg">{data.edge_simulation.availability_rate != null ? `${(data.edge_simulation.availability_rate * 100).toFixed(1)}%` : 'Unavailable'}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">Battery-Limited</div>
                  <div className="font-medium text-lg text-amber-400">{data.edge_simulation.battery_limited_clients || 0}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">Slowest Profile</div>
                  <div className="font-medium text-lg capitalize">{data.edge_simulation.slowest_device_profile || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">Edge Stragglers</div>
                  <div className="font-medium text-lg text-red-400">{data.edge_simulation.edge_stragglers || 0}</div>
                </div>
              </div>
            </div>
          </MotionCard>
        </motion.div>
      )}


      {/* 4. Model Performance Charts */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Global Performance" description="Accuracy and F1 Score across training rounds.">
          <PerformanceLineChart
            data={rounds}
            dataKeyX="round"
            lines={[
              { key: 'accuracy', name: 'Accuracy', color: '#a5a0ff' },
              { key: 'f1', name: 'F1 Score', color: '#67c6ed' }
            ]}
          />
        </ChartCard>
        <ChartCard title="Reconstruction Loss" description="Reported autoencoder reconstruction loss by training round.">
          <PerformanceLineChart
            data={rounds}
            dataKeyX="round"
            lines={[
              { key: 'loss', name: 'Loss', color: '#ef4444' }
            ]}
          />
        </ChartCard>
      </motion.div>

      {/* 5. Anomaly Volume */}
      <motion.div variants={itemVariants}>
        <ChartCard title="Detected Anomalies" description="Anomaly volume detected by the global model over the last 24 hours.">
          <AnomalyAreaChart
            data={anomalies}
            dataKeyX="time"
            dataKeyY="volume"
            color="#f59e0b"
          />
        </ChartCard>
      </motion.div>

      {/* 6. Recent Security Events + Recent Experiments */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Security Feed */}
        <MotionCard className="p-0 overflow-hidden flex flex-col">
          <div className="p-6 border-b border-border bg-muted/50">
            <h3 className="text-lg font-semibold text-foreground">Recent Security Events</h3>
          </div>
          <div className="p-0 flex-1 overflow-auto max-h-[400px]">
            {securityEvents.length === 0 && <DataState title="No recent security events" description="No events were returned for this overview." />}
            <ul className="divide-y divide-border">
              {securityEvents.map(event => (
                <li key={event.id} className="p-4 hover:bg-muted transition-colors">
                  <div className="flex items-start gap-3">
                    <div className={`mt-0.5 p-1.5 rounded-md ${
                      event.severity === 'critical' ? 'bg-red-500/10 text-red-300' :
                      event.severity === 'high' ? 'bg-orange-500/10 text-orange-300' :
                      event.severity === 'medium' ? 'bg-amber-500/10 text-amber-300' :
                      'bg-blue-500/10 text-blue-300'
                    }`}>
                      <ShieldAlert className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-medium text-sm text-foreground">{event.eventType}</span>
                        <span className="text-xs text-muted-foreground">{event.timestamp}</span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{event.message}</p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </MotionCard>

        {/* Recent Experiments */}
        <MotionCard className="p-0 overflow-hidden flex flex-col">
          <div className="p-6 border-b border-border bg-muted/50">
            <h3 className="text-lg font-semibold text-foreground">Recent Experiments</h3>
          </div>
          <div className="p-0 flex-1 overflow-auto max-h-[400px]">
            {experiments.length === 0 && <DataState title="No recent experiments" />}
            <table aria-label="Recent experiments" className="w-full text-sm text-left">
              <thead className="text-muted-foreground"><tr><th className="px-6 py-3">Experiment</th><th className="px-6 py-3">Accuracy</th><th className="px-6 py-3">Date</th></tr></thead><tbody className="divide-y divide-border">
                {experiments.map(exp => (
                  <tr key={exp.id} className="hover:bg-muted transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-foreground">{exp.name}</div>
                      <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                        <GitCommit className="w-3 h-3" /> {exp.id}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-medium text-foreground">{exp.accuracy}</td>
                    <td className="px-6 py-4 text-right text-muted-foreground">{exp.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </MotionCard>
      </motion.div>

      {/* 7. System Status */}
      <motion.div variants={itemVariants}>
        <MotionCard className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">System Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systemStatus.length === 0 && <DataState title="Service health unavailable" />}
            {systemStatus.map(sys => (
              <div key={sys.name} className="flex items-center gap-3 p-3 rounded-lg border border-border bg-muted/50">
                {sys.status === 'operational' ? (
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                ) : sys.status === 'degraded' ? (
                  <AlertCircle className="w-5 h-5 text-amber-500" />
                ) : sys.status === 'offline' ? (
                  <XCircle className="w-5 h-5 text-red-500" />
                ) : (
                  <HelpCircle className="w-5 h-5 text-muted-foreground" />
                )}
                <div>
                  <div className="font-medium text-sm text-foreground">{sys.name}</div>
                  <div className="text-xs text-muted-foreground capitalize">
                    {sys.detail || sys.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </MotionCard>
      </motion.div>

    </motion.div>
  );
}
