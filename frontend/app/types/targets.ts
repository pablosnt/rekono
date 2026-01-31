import type { DefectDojoSync } from "./defectdojo";

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
