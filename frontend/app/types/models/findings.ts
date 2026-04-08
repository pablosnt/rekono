import type { Execution } from "./scans";

export interface Finding {
  id: number;
  project: number;
  executions: Execution[];
  is_fixed: boolean;
  auto_fixed: boolean;
  fixed_date: string;
  fixed_by?: { id: number; username: string };
  defectdojo_id?: number;
  hacktricks_link?: string;
  created_from_user_input: boolean;
  triage_status?: string;
  triage_comment?: string;
  triage_date?: string;
  triage_by?: { id: number; username: string };
}
