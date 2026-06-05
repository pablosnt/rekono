export interface FindingsEvolution {
  month: string;
  discovered: number;
  fixed: number;
  active: number;
}

export interface BarSeries {
  label: string;
  color: string | ((d: unknown) => string);
  legendColor?: string;
  y: (d: unknown) => number;
}
