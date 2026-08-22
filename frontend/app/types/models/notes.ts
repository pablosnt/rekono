export interface Note {
  id: number;
  project: number;
  target?: { id: number; project: number; target: string; type: string };
  task?: { id: number };
  osint?: { id: number; data: string; data_type: string; source?: string };
  host?: { id: number; ip: string; domain?: string };
  port?: {
    id: number;
    host?: { id: number; ip: string; domain?: string };
    port: number;
    protocol?: string;
    service?: string;
  };
  path?: {
    id: number;
    port?: {
      id: number;
      host?: number;
      port: number;
      protocol?: string;
      service?: string;
    };
    path: string;
    status?: number;
    type: string;
  };
  credential?: { id: number; email?: string; username?: string };
  technology?: {
    id: number;
    port?: {
      id: number;
      port: number;
      host?: { id: number; ip: string; domain?: string };
    };
    name: string;
    version?: string;
  };
  vulnerability?: { id: number; name: string; severity: string; cve?: string };
  exploit?: {
    id: number;
    vulnerability?: number;
    technology?: {
      id: number;
      port?: {
        id: number;
        port: number;
        host?: { id: number; ip: string; domain?: string };
      };
      name: string;
      version?: string;
    };
    title: string;
    edb_id?: number;
  };
  title: string;
  body?: string;
  tags: string[];
  owner?: { id: number; username: string };
  public: boolean;
  forked: boolean;
  forked_from?: number;
  forks: number[];
  created_at: string;
  updated_at: string;
  liked: boolean;
  likes: number;
}
