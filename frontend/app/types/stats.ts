export interface FindingsEvolution {
  month: string;
  discovered: number;
  fixed: number;
  active: number;
}

export interface BarSeries {
  label: string;
  color: string;
  y: (d: unknown) => number;
}
