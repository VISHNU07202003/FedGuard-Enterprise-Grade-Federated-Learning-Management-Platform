import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/apiClient';

export const useDashboardSummary = () => {
  return useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: () => dashboardService.getSummary(),
    refetchInterval: 5000 // Poll every 5 seconds for simulation updates
  });
};
