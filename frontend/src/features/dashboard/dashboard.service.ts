import {
  DashboardMetric,
  TrainingRoundMetric,
  AnomalyVolumeMetric,
  TrainingRunSummary,
  ClientHealthSummary,
  SecurityEvent,
  ExperimentSummary,
  SystemServiceStatus,
  mockDashboardMetrics,
  mockTrainingRounds,
  mockAnomalyVolume,
  mockTrainingRuns,
  mockClients,
  mockSecurityEvents,
  mockModels,
  mockSystemStatus
} from '@/lib/mock-data';

/**
 * Dashboard Service Layer
 * 
 * Currently returns mock data to support UI development (Phase 3).
 * Will be updated to make real API calls in Phase 6.
 */

export async function getDashboardMetrics(): Promise<DashboardMetric[]> {
  return Promise.resolve(mockDashboardMetrics);
}

export async function getTrainingRounds(): Promise<TrainingRoundMetric[]> {
  return Promise.resolve(mockTrainingRounds);
}

export async function getAnomalyVolume(): Promise<AnomalyVolumeMetric[]> {
  return Promise.resolve(mockAnomalyVolume);
}

export async function getRecentTrainingRuns(): Promise<TrainingRunSummary[]> {
  return Promise.resolve(mockTrainingRuns.slice(0, 5));
}

export async function getClientHealth(): Promise<ClientHealthSummary[]> {
  return Promise.resolve(mockClients);
}

export async function getRecentSecurityEvents(): Promise<SecurityEvent[]> {
  return Promise.resolve(mockSecurityEvents);
}

export async function getRecentExperiments(): Promise<ExperimentSummary[]> {
  return Promise.resolve(mockModels.slice(0, 4));
}

export async function getSystemStatus(): Promise<SystemServiceStatus[]> {
  return Promise.resolve(mockSystemStatus);
}
