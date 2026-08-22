export interface User {
  id: number;
  username: string;
  email?: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
  last_login: string;
  role: string;
}
