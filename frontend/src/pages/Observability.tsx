import { motion } from 'framer-motion';
import { MotionCard } from '@/components/ui/card';
import { Activity, Database, Server, Zap } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const GRAFANA_URL = import.meta.env.VITE_GRAFANA_URL ?? 'http://localhost:3000';
const PROMETHEUS_URL = import.meta.env.VITE_PROMETHEUS_URL ?? 'http://localhost:9090';
const METRICS_URL = import.meta.env.VITE_METRICS_URL ?? 'http://localhost:8000/metrics';

export function Observability() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="max-w-7xl mx-auto space-y-8"
    >
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Observability</h1>
          <p className="text-muted-foreground mt-1">System health, metrics, and telemetry.</p>
        </div>
        <Badge variant="secondary" className="text-sm px-3 py-1">
          <Activity className="w-4 h-4 mr-2" /> Monitoring tools
        </Badge>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {/* Grafana */}
        <MotionCard className="p-6 flex flex-col items-start gap-4">
          <div className="w-12 h-12 bg-orange-500/10 text-orange-300 rounded-xl flex items-center justify-center">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">Grafana Dashboards</h3>
            <p className="text-sm text-muted-foreground mt-1">View comprehensive visualizations for API, Federation, and Edge Simulator metrics.</p>
          </div>
          <a href={GRAFANA_URL} target="_blank" rel="noreferrer" className="mt-auto px-4 py-2 bg-slate-900 text-white rounded-md text-sm font-medium hover:bg-slate-800 transition-colors w-full text-center">
            Open Grafana
          </a>
        </MotionCard>

        {/* Prometheus */}
        <MotionCard className="p-6 flex flex-col items-start gap-4">
          <div className="w-12 h-12 bg-red-500/10 text-red-300 rounded-xl flex items-center justify-center">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">Prometheus Server</h3>
            <p className="text-sm text-muted-foreground mt-1">Direct access to the time-series database scraping our FastAPI endpoints.</p>
          </div>
          <a href={PROMETHEUS_URL} target="_blank" rel="noreferrer" className="mt-auto px-4 py-2 border border-border text-foreground rounded-md text-sm font-medium hover:bg-muted transition-colors w-full text-center">
            Open Prometheus
          </a>
        </MotionCard>

        {/* Metrics Endpoint */}
        <MotionCard className="p-6 flex flex-col items-start gap-4">
          <div className="w-12 h-12 bg-blue-500/10 text-blue-300 rounded-xl flex items-center justify-center">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">FastAPI Metrics</h3>
            <p className="text-sm text-muted-foreground mt-1">Raw Prometheus exposition format metrics directly from the backend server.</p>
          </div>
          <a href={METRICS_URL} target="_blank" rel="noreferrer" className="mt-auto px-4 py-2 border border-border text-foreground rounded-md text-sm font-medium hover:bg-muted transition-colors w-full text-center">
            View /metrics
          </a>
        </MotionCard>

      </div>

      <MotionCard className="p-6">
        <h3 className="text-lg font-semibold text-foreground flex items-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-indigo-500" />
          Monitored Telemetry Scope
        </h3>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-8 text-sm text-muted-foreground list-disc pl-5">
          <li><strong>API Performance:</strong> Request rates, P95 latencies, error codes, and active connection gauges.</li>
          <li><strong>Federation Pipeline:</strong> Round completions, client dropouts, stragglers, and aggregation times.</li>
          <li><strong>Edge Simulation:</strong> Device latency averages, battery skip events, and connectivity faults.</li>
          <li><strong>Privacy Controls:</strong> Epsilon expenditure, noise multipliers, and DP-SGD activation stats.</li>
          <li><strong>Security & Copilot:</strong> RBAC denials, guardrail blocks, and AI query response times.</li>
          <li><strong>WebSockets:</strong> Real-time event emits and active socket tracking.</li>
        </ul>
        <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg text-sm text-blue-300">
          <strong>Note on MLflow:</strong> Prometheus/Grafana is explicitly configured for operational system health. For deep model experimentation, artifact lineage, and parameter tuning comparisons, continue using the MLflow Tracking UI.
        </div>
      </MotionCard>
    </motion.div>
  );
}
