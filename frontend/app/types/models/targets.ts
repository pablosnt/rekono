import type { Authentication } from "./authentications";
import type { DefectDojoSync } from "./integrations";

export interface TargetPort {
  id: number;
  target: number;
  port: number;
  path: string;
  authentication: Authentication;
}

export interface TargetDenylist {
  id: number;
  target: string;
  default: boolean;
}

export interface Target {
  id: number;
  project: number;
  target: string;
  type: string;
  defectdojo_sync: DefectDojoSync;
  target_ports: Array<number>;
  tasks: Array<number>;
  notes: Array<number>;
  reports: Array<number>;
}
