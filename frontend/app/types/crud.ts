import type { TableColumn } from "@nuxt/ui";
import type { BreadcrumbItem } from "@nuxt/ui";

export interface FilterOption {
  label: string;
  value: unknown;
}

export interface FilterConfig {
  key: string;
  label: string;
  type: "select" | "multiselect" | "text" | "date" | "daterange" | "boolean";
  options?: FilterOption[] | (() => Promise<FilterOption[]>);
  placeholder?: string;
  icon?: string;
}

export interface CardConfig {
  title: string;
  description?: string;
  icon?: string;
  avatar?: {
    text: string;
    class?: string;
  };
  badges?: Array<{
    label: string;
    color: string;
  }>;
  meta?: Array<{
    label: string;
    value: string;
    icon?: string;
  }>;
  to?: string;
}

export interface CrudConfig<T = unknown> {
  endpoint: string;
  entityName: string;
  entityNamePlural: string;

  tableColumns?: TableColumn<T>[];
  tableColumnsVisibility?: Record<string, boolean>;
  cardFormatter?: (item: T) => CardConfig;

  breadcrumbs?: BreadcrumbItem[];
  searchable: boolean;
  searchPlaceholder?: string;
  filters?: FilterConfig[];
  ordering?: string[];
  defaultOrdering: string;

  canRead: boolean;
  canCreate: boolean;
  canEdit: boolean;
  canDelete: boolean;
  deleteMessage?: string;

  pageSize?: number;
  pageSizeOptions?: number[];
}

export interface CrudState<T = unknown> {
  items: T[];
  total: number;
  loading: boolean;
  page: number;
  pageSize: number;
  searchQuery?: string;
  filters: Record<string, unknown>;
  ordering: string;
}
