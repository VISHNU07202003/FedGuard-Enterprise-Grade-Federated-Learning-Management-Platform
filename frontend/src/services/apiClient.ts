import {
  mockTrainingRounds,
  mockAnomalyVolume,
  mockClients,
  mockSecurityEvents,
  mockModels,
  mockSystemStatus,
  SecurityEvent,
  ExperimentSummary,
  SystemServiceStatus
} from '../lib/mock-data';

export interface KPIMetrics {
  total_clients: number;
  active_training_runs: number;
  anomalies_detected_24h: number;
  system_health_score: number;
}

export interface ClientHealthSummary {
  online: number;
  offline: number;
  training: number;
  error: number;
}

export interface DashboardSummaryResponse {
  system_status: { status: string; message: string; }[];
  kpi_metrics: KPIMetrics;
  current_training_run: any;
  client_health_summary: ClientHealthSummary;
  model_performance_series: any[];
  anomalies: any[];
  recent_security_events: SecurityEvent[];
  recent_experiments: ExperimentSummary[];
  service_health: SystemServiceStatus[];
  edge_simulation?: {
    enabled: boolean;
    active_edge_clients: number;
    average_latency_ms?: number;
    availability_rate?: number;
    battery_limited_clients: number;
    slowest_device_profile?: string;
    edge_stragglers: number;
  };
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = import.meta.env.VITE_USE_MOCK_DATA === 'true';

export const dashboardService = {
  getSummary: async (): Promise<DashboardSummaryResponse> => {
    if (USE_MOCK) {
      return {
        system_status: [{status: 'operational', message: 'All systems go'}],
        kpi_metrics: {
          total_clients: mockClients.length,
          active_training_runs: 1,
          anomalies_detected_24h: mockAnomalyVolume.reduce((acc, curr) => acc + curr.volume, 0),
          system_health_score: 98
        },
        current_training_run: {
          run_id: "fed-run-482a",
          status: "running",
          current_round: 18,
          total_rounds: 50
        },
        client_health_summary: {
          online: mockClients.filter(c => c.status === 'online').length,
          offline: mockClients.filter(c => c.status === 'offline').length,
          training: mockClients.filter(c => c.status === 'syncing').length,
          error: 0
        },
        model_performance_series: mockTrainingRounds,
        anomalies: mockAnomalyVolume,
        recent_security_events: mockSecurityEvents,
        recent_experiments: mockModels,
        service_health: mockSystemStatus
      };
    }
    
    const token = localStorage.getItem('token');

const response = await fetch(`${API_URL}/api/v1/dashboard/`, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    return response.json();
  }
};
