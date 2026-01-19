import type { TableColumn, BreadcrumbItem } from "@nuxt/ui";
import type * as z from "zod";

export interface FilterOption {
  label: string;
  value: unknown;
  avatar?: { src?: string; text?: string; class?: string };
  icon?: string;
}

export interface FormField {
  key: string;
  label: string;
  type:
    | "text"
    | "number"
    | "textarea"
    | "select"
    | "multiselect"
    | "checkbox"
    | "tags"
    | "file";
  required?: boolean;
  placeholder?: string;
  hint?: string;
  icon?: string;
  avatar?: Record<string, unknown>;
  options?: FilterOption[];
  clearable?: boolean;
  accept?: string;
  fileSize?: number;
  fileUploadLabel?: string;
  fileUploadDescription?: string;
}

export interface FilterConfig {
  key: string;
  label: string;
  value?: unknown;
  type: "select" | "text" | "boolean" | "range";
  options?: FilterOption[] | (() => Promise<FilterOption[]>);
  placeholder?: string;
  icon?: string;
  min?: number;
  max?: number;
  step?: number;
  multiple?: boolean;
}

export type CrudTableColumn<T> = TableColumn<T> & {
  icon?: string;
};

export interface ComponentDetails {
  component: unknown;
  props?: Record<string, unknown>;
}

export interface CrudConfig<T = unknown> {
  endpoint: string;
  entityName: string;
  entityNamePlural: string;
  icon?: string;
  breadcrumbs?: BreadcrumbItem[];
  tableColumns?: CrudTableColumn<T>[];
  tableColumnsVisibility?: Record<string, boolean>;
  useGrid?: boolean;
  itemLink?: (item: T) => string;
  onItemClick?: (item: T) => void;
  searchable: boolean;
  searchPlaceholder?: string;
  filters?: FilterConfig[];
  ordering?: Array<string | { id: string; label: string }>;
  defaultOrdering: string;
  pageSize?: number;
  pageSizeOptions?: number[];
  formFields?: FormField[];
  formSchema?: z.ZodType;
  formFullscreen?: boolean;
  createFormFields?: FormField[];
  createFormSchema?: z.ZodType;
  createForm?: object;
  updateOnCreateModalOpen?: boolean;
  onCreation?: (data: Record<string, unknown>) => void;
  editFormFields?: FormField[];
  editFormSchema?: z.ZodType;
  editForm?: object;
  updateOnEditModalOpen?: boolean;
  modalIcon?: string | ((item: T) => string);
  modalIconClass?: string;
  modalAvatar?: (item: T) => Record<string, unknown>;
  deleteMessage?: (item: T) => ComponentDetails[];
  deleteVerb?: string;
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
