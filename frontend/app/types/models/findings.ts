import type { Execution } from "./scans";

export interface Finding {
  id: number;
  project: number;
  executions: Execution[];
  is_fixed: boolean;
  auto_fixed: boolean;
  fixed_date: string;
  fixed_by?: { id: number; username: string };
  hacktricks_link?: string;
  created_from_user_input: boolean;
  triage_status?: string;
  triage_comment?: string;
  triage_date?: string;
  triage_by?: { id: number; username: string };
  notes: number[];
}

export interface OSINT extends Finding {
  data: string;
  data_type: string;
  source?: string;
}

export interface HostBase extends Finding {
  ip: string;
  domain?: string;
  os?: string;
  os_type: string;
  country?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  reputation?: number;
  malicious_analysis?: number;
  suspicious_analysis?: number;
  total_analysis?: number;
  whois?: string;
  port: number[];
}

export interface PortBase extends Finding {
  host?: number;
  port: number;
  status: string;
  protocol?: string;
  service?: string;
  path: number[];
  technology: number[];
  vulnerability: number[];
}

export interface Host extends HostBase {
  port: PortBase[];
}

export interface Port extends PortBase {
  host?: HostBase;
}

export interface Path extends Finding {
  port?: Port;
  path: string;
  status?: number;
  extra_info?: string;
  type: string;
}

export interface CredentialBase extends Finding {
  technology?: number;
  email?: string;
  username?: string;
  secret?: string;
  context?: string;
}

export interface Technology extends Finding {
  port?: Port;
  name: string;
  version?: string;
  description?: string;
  reference?: string;
  credential: CredentialBase[];
  vulnerability: number[];
  exploit: number[];
}

export interface Credential extends CredentialBase {
  technology?: Technology;
}

export interface Vulnerability extends Finding {
  port?: Port;
  technology?: Technology;
  name: string;
  description?: string;
  severity: number;
  cvss_version?: string;
  cvss_vector?: string;
  cvss_base_score?: number;
  cve?: string;
  euvd_id?: string;
  ghsa_id?: string;
  osv_generic_id?: string;
  cwes: string[];
  epss_score?: number;
  epss_percentile?: number;
  remediation?: string;
  reference?: string;
  trending: boolean;
  exploit: number[];
}

export interface Exploit extends Finding {
  vulnerability?: Vulnerability;
  technology?: Technology;
  title: string;
  edb_id?: number;
  reference?: string;
}
