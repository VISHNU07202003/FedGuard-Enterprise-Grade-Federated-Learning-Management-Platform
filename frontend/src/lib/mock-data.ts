// ============================================================================
// Types
// ============================================================================

export type ClientStatus = 'online' | 'offline' | 'syncing';
export type SecuritySeverity = 'info' | 'low' | 'medium' | 'high' | 'critical';
export type ServiceStatus = 'operational' | 'degraded' | 'offline' | 'not_configured';

export interface DashboardMetric {
  title: string;
  value: string;
  trend?: string;
  trendUp?: boolean;
}

export interface TrainingRoundMetric {
  round: number;
  accuracy: number;
  loss: number;
  f1: number;
}

export interface AnomalyVolumeMetric {
  time: string;
  volume: number;
}

export interface TrainingRunSummary {
  id: string;
  status: 'completed' | 'warning' | 'failed' | 'running';
  rounds: number;
  accuracy: string;
  date: string;
  duration: string;
}

export interface ClientHealthSummary {
  id: string;
  name: string;
  status: ClientStatus;
  type: string;
  location: string;
  lastPing: string;
  dataSize: string;
}

export interface SecurityEvent {
  id: string;
  timestamp: string;
  severity: SecuritySeverity;
  clientId: string | null;
  eventType: string;
  message: string;
  status: 'resolved' | 'active' | 'investigating';
}

export interface ExperimentSummary {
  id: string;
  name: string;
  tags: string[];
  accuracy: string;
  parameters: string;
  date: string;
}

export interface SystemServiceStatus {
  name: string;
  status: ServiceStatus;
  detail?: string;
}

// ============================================================================
// Mock Data
// ============================================================================

export const mockDashboardMetrics: DashboardMetric[] = [
  { title: "Active Clients", value: "47 / 50", trend: "3 offline" },
  { title: "Global Accuracy", value: "94.7%", trend: "+2.1% from last run", trendUp: true },
  { title: "F1 Score", value: "92.4%", trend: "+1.8%", trendUp: true },
  { title: "AUC", value: "0.982" },
  { title: "Privacy Budget", value: "ε = 3.2", trend: "Target: 5.0" },
  { title: "Training Round", value: "18 / 50", trend: "Running" },
];

export const mockTrainingRounds: TrainingRoundMetric[] = Array.from({ length: 18 }, (_, i) => {
  // Simulate an increasing accuracy and decreasing loss curve
  const progress = i / 18;
  return {
    round: i + 1,
    accuracy: 60 + (35 * Math.log10(1 + progress * 9)) + (Math.random() * 2 - 1),
    loss: 2.0 - (1.8 * Math.log10(1 + progress * 9)) + (Math.random() * 0.1),
    f1: 55 + (38 * Math.log10(1 + progress * 9)) + (Math.random() * 2 - 1),
  };
});

export const mockAnomalyVolume: AnomalyVolumeMetric[] = Array.from({ length: 24 }, (_, i) => ({
  time: `${String(i).padStart(2, '0')}:00`,
  volume: Math.floor(Math.random() * 50) + (i === 14 ? 150 : 0) // Spike at 14:00
}));

export const mockTrainingRuns: TrainingRunSummary[] = [
  { id: 'fed-run-482a', status: 'completed', rounds: 50, accuracy: '94.2%', date: '2 hours ago', duration: '45m 12s' },
  { id: 'fed-run-4829', status: 'completed', rounds: 50, accuracy: '93.8%', date: 'Yesterday', duration: '46m 03s' },
  { id: 'fed-run-4828', status: 'warning', rounds: 12, accuracy: '—', date: '2 days ago', duration: '11m 40s' },
  { id: 'fed-run-4827', status: 'failed', rounds: 3, accuracy: '—', date: '2 days ago', duration: '2m 15s' },
  { id: 'fed-run-4826', status: 'completed', rounds: 50, accuracy: '92.1%', date: '4 days ago', duration: '44m 50s' },
];

export const mockClients: ClientHealthSummary[] = [
  { id: 'client-edge-ny1', name: 'NYC Edge Node', status: 'online', type: 'Server', location: 'us-east-1', lastPing: '2s ago', dataSize: '1.2 GB' },
  { id: 'client-edge-ny2', name: 'NYC Edge Node 2', status: 'online', type: 'Server', location: 'us-east-1', lastPing: '5s ago', dataSize: '0.8 GB' },
  { id: 'client-iot-sf1', name: 'SF IoT Gateway', status: 'offline', type: 'Gateway', location: 'us-west-1', lastPing: '12m ago', dataSize: '450 MB' },
  { id: 'client-edge-ldn', name: 'LDN Edge Node', status: 'online', type: 'Server', location: 'eu-west-2', lastPing: '1s ago', dataSize: '2.1 GB' },
  { id: 'client-mobile-12', name: 'Mobile Node 12', status: 'syncing', type: 'Mobile', location: 'ap-northeast-1', lastPing: '1s ago', dataSize: '120 MB' },
];

export const mockSecurityEvents: SecurityEvent[] = [
  { id: 'sec-981', timestamp: '10m ago', severity: 'high', clientId: 'client-edge-tk1', eventType: 'Client update rejected', message: 'Suspicious gradient magnitude detected (L2 norm exceeded threshold).', status: 'active' },
  { id: 'sec-980', timestamp: '1h ago', severity: 'medium', clientId: 'client-iot-sf1', eventType: 'Client timeout', message: 'Client failed to submit weights within the round window.', status: 'resolved' },
  { id: 'sec-979', timestamp: '3h ago', severity: 'critical', clientId: 'client-unknown', eventType: 'Malformed update received', message: 'Unrecognized tensor shape in aggregation payload.', status: 'investigating' },
  { id: 'sec-978', timestamp: '1d ago', severity: 'low', clientId: 'client-mobile-12', eventType: 'Privacy budget warning', message: 'Client approaching cumulative ε limit for this session.', status: 'active' },
  { id: 'sec-977', timestamp: '2d ago', severity: 'high', clientId: 'client-edge-br1', eventType: 'Client quarantined', message: 'Repeated timeout failures led to automatic quarantine.', status: 'resolved' },
];

export const mockModels: ExperimentSummary[] = [
  { id: 'v1.4.0', name: 'Global Anomaly Model', tags: ['production', 'stable'], accuracy: '94.2%', parameters: '1.2M', date: '2 hours ago' },
  { id: 'v1.3.1', name: 'Global Anomaly Model', tags: ['archived'], accuracy: '93.8%', parameters: '1.2M', date: '1 week ago' },
  { id: 'v1.3.0', name: 'Global Anomaly Model', tags: ['archived'], accuracy: '92.4%', parameters: '1.2M', date: '2 weeks ago' },
  { id: 'exp-beta-1', name: 'Lightweight Edge CNN', tags: ['experimental'], accuracy: '89.1%', parameters: '450K', date: '3 days ago' },
];

export const mockSystemStatus: SystemServiceStatus[] = [
  { name: 'API Server', status: 'operational' },
  { name: 'PostgreSQL Database', status: 'operational' },
  { name: 'Federation Server', status: 'operational' },
  { name: 'MLflow Tracking', status: 'degraded', detail: 'High latency' },
  { name: 'WebSocket Gateway', status: 'operational' },
  { name: 'Bedrock Copilot', status: 'not_configured', detail: 'Mock mode / Not configured' },
];
