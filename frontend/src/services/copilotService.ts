import axios from 'axios';

export interface CopilotContext {
  run_id?: string;
  experiment_id?: string;
  page?: string;
  round_number?: number;
  security_event_id?: string;
  action?: string;
}

export interface CopilotSource {
  type: string;
  id: string;
}

export interface CopilotResponse {
  answer: string;
  mode: string;
  grounded: boolean;
  sources: CopilotSource[];
  warnings: string[];
  created_at: string;
}

export const copilotService = {
  chat: async (message: string, context?: CopilotContext): Promise<CopilotResponse> => {
    const token = localStorage.getItem('token');
    const response = await axios.post('/api/v1/copilot/chat', {
      message,
      context: context || {}
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  }
};