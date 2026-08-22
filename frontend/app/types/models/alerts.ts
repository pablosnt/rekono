export interface Alert {
  id: number;
  project: number;
  item: string;
  value?: string;
  enabled: boolean;
  subscribe_all_members?: boolean;
  owner?: {
    id: number;
    username: string;
  };
  subscribed: boolean;
  subscribers: number[];
}
