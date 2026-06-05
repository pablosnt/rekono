import type { DefectDojoSync } from "./integrations";

export interface Project {
  id: number;
  name: string;
  description: string;
  owner: {
    id: number;
    username: string;
  } | null;
  targets: Array<number>;
  members: Array<number>;
  tags: Array<string>;
  defectdojo_sync?: DefectDojoSync;
}
