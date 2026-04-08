import type { TargetPort } from "./targets";

export interface Task {
  id: number;
  target: {
    id: number;
    target: string;
    type: string;
  };
  process?: {
    id: number;
    name: string;
  };
  configuration?: {
    id: number;
    name: string;
    tool: {
      id: number;
      name: string;
      icon: string;
    };
  };
  intensity: string;
  executor: {
    id: number;
    username: string;
    email: string;
  };
  scheduled_at?: string;
  repeat_in?: number;
  repeat_time_unit?: string;
  start?: string;
  end?: string;
  target_port?: TargetPort;
  status: string;
  executions: number[];
  progress: number;
}

export interface Execution {
  id: number;
  configuration?: {
    id: number;
    name: string;
    tool: { id: number; name: string; icon?: string };
  };
  output_plain?: string;
  skipped_reason?: string;
  has_report: boolean;
  status: string;
  start?: string;
  end?: string;
  osint: number[];
  host: number[];
  port: number[];
  path: number[];
  technology: number[];
  credential: number[];
  vulnerability: number[];
  exploit: number[];
}
