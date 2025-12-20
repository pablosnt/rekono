import type { User } from "./users";
import type { Configuration } from "./tools";

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
