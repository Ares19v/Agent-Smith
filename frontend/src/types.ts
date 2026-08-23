export interface Message {
  id: string;
  sender: 'user' | 'bot' | 'system';
  text: string;
  agentName?: string;
  timestamp: string;
  isError?: boolean;
}

export interface AgentDetails {
  name: string;
  is_trained: boolean;
  intent_count: number;
  intents: string[];
  patterns_map?: Record<string, string[]>;
  responses_map?: Record<string, string[]>;
  total_patterns?: number;
  memory: Array<{ user: string; bot: string }>;
}

export interface DocumentContextInfo {
  filename: string | null;
  loaded: boolean;
  size_kb?: number;
  preview?: string;
}

export interface HealthStatus {
  status: string;
  agents_loaded: number;
  document_loaded: boolean;
  document_filename: string | null;
}
