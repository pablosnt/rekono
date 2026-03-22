export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
  last_login: string;
  role: string;
}

export interface ApiToken {
  name: string;
  expiration?: string;
  key?: string;
}

export interface Authentication {
  id: number;
  name: string;
  secret: string;
  type: string;
  target_port: number;
}

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

export interface Intensity {
  id: number;
  argument: string;
  value: number;
}

export interface Configuration {
  id: number;
  name: string;
  stage: string;
  default: boolean;
  deprecated: boolean;
}

export interface Tool {
  id: number;
  name: string;
  command?: string;
  script?: string;
  is_installed?: boolean;
  version?: string;
  reference?: string;
  icon?: string;
  liked: boolean;
  likes: number;
  intensities: Intensity[];
  configurations: Configuration[];
}

export interface Step {
  id: number;
  process: number;
  configuration: Configuration;
}

export interface Process {
  id: number;
  name: string;
  description: string;
  owner: User | null;
  liked: boolean;
  likes: number;
  steps: Step[];
  tags: string[];
  wordlists: {
    required: boolean;
    supported: boolean;
  };
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
}

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

export enum WordlistType {
  ENDPOINT = "Endpoint",
  SUBDOMAIN = "Subdomain",
}

export interface Wordlist {
  id: number;
  name: string;
  type: WordlistType;
  size: number;
  owner?: {
    id: number;
    username: string;
  };
  liked: boolean;
  likes: number;
}

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
