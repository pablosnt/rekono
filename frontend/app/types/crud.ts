import type { TableColumn, FormField, BreadcrumbItem } from "@nuxt/ui";
import type * as z from "zod";

export interface FilterOption {
  label: string;
  value: unknown;
}

export interface FilterConfig {
  key: string;
  label: string;
  value?: unknown;
  type: "select" | "text" | "boolean";
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

export type CrudTableColumn<T> = TableColumn<T> & {
  icon?: string;
};

export interface DeleteDetail {
  text: string;
  class?: string;
}

export interface CrudConfig<T = unknown> {
  endpoint: string;
  entityName: string;
  entityNamePlural: string;
  icon?: string;
  breadcrumbs?: BreadcrumbItem[];
  tableColumns?: CrudTableColumn<T>[];
  tableColumnsVisibility?: Record<string, boolean>;
  cardFormatter?: (item: T) => CardConfig;
  searchable: boolean;
  searchPlaceholder?: string;
  filters?: FilterConfig[];
  ordering?: string[];
  defaultOrdering: string;
  pageSize?: number;
  pageSizeOptions?: number[];
  formFields?: FormField[];
  formSchema?: z.ZodType;
  deleteMessage?: (item: T) => DeleteDetail[];
  canRead: boolean;
  canCreate: boolean;
  canEdit: boolean | ((item: T) => boolean);
  canDelete: boolean | ((item: T) => boolean);
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
