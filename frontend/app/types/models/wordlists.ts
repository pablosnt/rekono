export interface Wordlist {
  id: number;
  name: string;
  type: "Endpoint" | "Subdomain";
  size: number;
  owner?: {
    id: number;
    username: string;
  };
  liked: boolean;
  likes: number;
}
