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
