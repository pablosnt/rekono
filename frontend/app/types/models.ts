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
