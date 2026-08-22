export interface Report {
  id: number;
  project?: number;
  target?: {
    id: number;
    target: string;
  };
  task?: {
    id: number;
  };
  status: string;
  format: string;
  user?: {
    id: number;
    username: string;
  };
  date: string;
}
