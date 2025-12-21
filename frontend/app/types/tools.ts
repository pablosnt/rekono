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
  liked?: boolean;
  likes?: number;
  intensities?: Intensity[];
  configurations?: Configuration[];
}
