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

  if (isLoading) return <div className="p-8 text-muted-foreground">Loading dashboard data...</div>;
  if (isError) return <div className="p-8 text-red-500">Error loading dashboard data.</div>;
  if (!data) return null;

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
      <motion.div variants={itemVariants} className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Real-time overview of your federated learning network.</p>
        </div>
        <div className="flex items-center gap-2">
           {wsStatus === 'connected' && <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50"><span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"></span>Live</Badge>}
           {wsStatus === 'reconnecting' && <Badge variant="outline" className="text-amber-600 border-amber-200 bg-amber-50">Reconnecting...</Badge>}
           {(wsStatus === 'disconnected' || wsStatus === 'error') && runId && <Badge variant="outline" className="text-slate-500">Offline</Badge>}
        </div>
      </motion.div>

      {/* 2. KPI Cards */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MotionCard className="p-6">
          <h3 className="text-sm font-medium text-muted-foreground">Total Clients</h3>
          <p className="text-3xl font-bold mt-2">{kpi_metrics.total_clients}</p>
        </MotionCard>
        <MotionCard className="p-6">
          <h3 className="text-sm font-medium text-muted-foreground">Active Runs</h3>
          <p className="text-3xl font-bold mt-2">{kpi_metrics.active_training_runs}</p>
        </MotionCard>
        <MotionCard className="p-6">
          <h3 className="text-sm font-medium text-muted-foreground">Anomalies (24h)</h3>
          <p className="text-3xl font-bold mt-2">{kpi_metrics.anomalies_detected_24h}</p>
        </MotionCard>
        <MotionCard className="p-6">
          <h3 className="text-sm font-medium text-muted-foreground">System Score</h3>
          <p className="text-3xl font-bold mt-2">{kpi_metrics.system_health_score}/100</p>
        </MotionCard>
      </motion.div>

      {/* 3. Training Run & Client Health */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <MotionCard className="p-6 col-span-2">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground">Current Training Run</h3>
              <p className="text-sm text-muted-foreground">run-id: {current_training_run?.run_id || 'None'}</p>
              
              <div className="mt-2 flex flex-col gap-2">
                {current_training_run?.mlflow_run_id && (
                  <div className="flex items-center">
                    <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50">
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
                      <span className="ml-2 text-xs text-slate-400" title={`Local tracking: ${current_training_run.mlflow_tracking_uri}`}>(Local File tracking)</span>
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
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="font-medium text-foreground">
                Round {Math.max(liveRound, current_training_run?.current_round || 0)} of {current_training_run?.total_rounds || 0}
              </span>
              <span className="text-muted-foreground">
                {current_training_run ? Math.round((Math.max(liveRound, current_training_run.current_round) / current_training_run.total_rounds) * 100) : 0}% Complete
              </span>
            </div>
            <Progress value={current_training_run ? (Math.max(liveRound, current_training_run.current_round) / current_training_run.total_rounds) * 100 : 0} className="h-2" />
          </div>
        </MotionCard>

        <MotionCard className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Reliability & Client Health</h3>
          
          <div className="mb-4 p-3 bg-slate-50 border border-border rounded-lg space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Round Status</span>
              <Badge variant={liveStatus === 'running' ? 'success' : 'secondary'} className="capitalize">{liveStatus || 'Idle'}</Badge>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Clients Online</span>
              <span className="font-medium text-foreground">{client_health_summary.online}</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Rejections</span>
              <span className="font-medium text-amber-600">0</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Stragglers</span>
              <span className="font-medium text-blue-600">0</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Dropout Rate</span>
              <span className="font-medium text-foreground">0%</span>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-slate-700">
                <span className="w-2.5 h-2.5 rounded-full bg-green-500" /> Online
              </div>
              <span className="font-medium">{client_health_summary.online}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-slate-700">
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
                  <div className="text-slate-400 mb-1">Active Edge Clients</div>
                  <div className="font-medium text-lg">{data.edge_simulation.active_edge_clients || 0}</div>
                </div>
                <div>
                  <div className="text-slate-400 mb-1">Average Latency</div>
                  <div className="font-medium text-lg">{data.edge_simulation.average_latency_ms || 0} ms</div>
                </div>
                <div>
                  <div className="text-slate-400 mb-1">Availability Rate</div>
                  <div className="font-medium text-lg">{data.edge_simulation.availability_rate ? `${(data.edge_simulation.availability_rate * 100).toFixed(1)}%` : '0%'}</div>
                </div>
                <div>
                  <div className="text-slate-400 mb-1">Battery-Limited</div>
                  <div className="font-medium text-lg text-amber-400">{data.edge_simulation.battery_limited_clients || 0}</div>
                </div>
                <div>
                  <div className="text-slate-400 mb-1">Slowest Profile</div>
                  <div className="font-medium text-lg capitalize">{data.edge_simulation.slowest_device_profile || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-slate-400 mb-1">Edge Stragglers</div>
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
              { key: 'accuracy', name: 'Accuracy', color: '#4f46e5' },
              { key: 'f1', name: 'F1 Score', color: '#0ea5e9' }
            ]} 
          />
        </ChartCard>
        <ChartCard title="Reconstruction Loss" description="Average autoencoder loss decreasing over time.">
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
          <div className="p-6 border-b border-border bg-slate-50/50">
            <h3 className="text-lg font-semibold text-foreground">Recent Security Events</h3>
          </div>
          <div className="p-0 flex-1 overflow-y-auto max-h-[400px]">
            <ul className="divide-y divide-border">
              {securityEvents.map(event => (
                <li key={event.id} className="p-4 hover:bg-slate-50 transition-colors">
                  <div className="flex items-start gap-3">
                    <div className={`mt-0.5 p-1.5 rounded-md ${
                      event.severity === 'critical' ? 'bg-red-100 text-red-700' :
                      event.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                      event.severity === 'medium' ? 'bg-amber-100 text-amber-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      <ShieldAlert className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm text-foreground">{event.eventType}</span>
                        <span className="text-xs text-muted-foreground">{event.timestamp}</span>
                      </div>
                      <p className="text-sm text-slate-600 mt-1">{event.message}</p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </MotionCard>

        {/* Recent Experiments */}
        <MotionCard className="p-0 overflow-hidden flex flex-col">
          <div className="p-6 border-b border-border bg-slate-50/50">
            <h3 className="text-lg font-semibold text-foreground">Recent Experiments</h3>
          </div>
          <div className="p-0 flex-1 overflow-y-auto max-h-[400px]">
            <table className="w-full text-sm text-left">
              <tbody className="divide-y divide-border">
                {experiments.map(exp => (
                  <tr key={exp.id} className="hover:bg-slate-50 transition-colors">
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
            {systemStatus.map(sys => (
              <div key={sys.name} className="flex items-center gap-3 p-3 rounded-lg border border-border bg-slate-50/50">
                {sys.status === 'operational' ? (
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                ) : sys.status === 'degraded' ? (
                  <AlertCircle className="w-5 h-5 text-amber-500" />
                ) : sys.status === 'offline' ? (
                  <XCircle className="w-5 h-5 text-red-500" />
                ) : (
                  <HelpCircle className="w-5 h-5 text-slate-400" />
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
