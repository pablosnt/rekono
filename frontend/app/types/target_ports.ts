import type { Authentication } from "./authentication";

export interface TargetPort {
  id: number;
  target: number;
  port: number;
  path: string;
  authentication: Authentication;
}
