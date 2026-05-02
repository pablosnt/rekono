export interface DefectDojoSync {
  id: number;
  project: number;
  product_id: number;
  engagement_id: number;
  reimport: boolean;
  close_old_findings: boolean;
}

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
