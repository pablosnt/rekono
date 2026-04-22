export interface DefectDojoSync {
  id: number;
  defectdojo_sync: number;
  target: number;
  engagement_id: number;
}

export interface Integration {
  id: number;
  name: string;
  description: string;
  enabled: boolean;
  reference: string;
  icon?: string;
}

export interface DefectDojoSettings {
  server: string;
  api_token: string;
  tls_validation: boolean;
  tag: string;
  test_type: string;
  test: string;
  is_available: boolean;
}

export interface NvdNistSettings {
  api_token: string;
  is_available?: boolean;
}

export interface CveCrowdSettings {
  api_token: string;
  trending_span_days: number;
  execute_per_execution: boolean;
  is_available?: boolean;
}

export interface VirusTotalSettings {
  api_token: string;
  is_available: boolean;
}

export interface SmtpSettings {
  host: string;
  port: number;
  username: string;
  password: string;
  tls: boolean;
  is_available: boolean;
}

export interface TelegramSettings {
  token: string;
  bot: string;
  is_available: boolean;
}
