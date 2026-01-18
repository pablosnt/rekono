export interface Integration {
  id: number;
  name: string;
  description: string;
  enabled: boolean;
  reference: string;
  icon?: string;
}