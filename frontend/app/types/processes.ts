import type { User } from "./users";

export interface Step {
  id: number;
  process: number;
  configuration_id: number;
  configuration: any;
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
  [key: string]: any;
}
