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
