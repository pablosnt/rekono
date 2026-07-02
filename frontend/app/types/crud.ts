import type { TableColumn } from "@nuxt/ui";
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
    | "file"
    | "datetime";
  required?: boolean;
  disabled?: boolean;
  hidden?: boolean;
  placeholder?: string;
  hint?: string;
  size?: string;
  icon?: string;
  avatar?: Record<string, unknown>;
  options?: FilterOption[];
  clearable?: boolean;
  accept?: string;
  fileSize?: number;
  fileUploadLabel?: string;
  fileUploadDescription?: string;
  minValue?: unknown;
  maxValue?: unknown;
  initialCalendarDate?: unknown;
  valueKey?: string;
  labelKey?: string;
  inputMode?: string;
}

export interface FilterConfig {
  key: string;
  label: string;
  value?: unknown;
  type: "select" | "text" | "boolean" | "range";
  valueKey?: string;
  labelKey?: string;
  options?: FilterOption[] | (() => Promise<FilterOption[]>);
  placeholder?: string;
  icon?: string;
  min?: number;
  max?: number;
  step?: number;
  multiple?: boolean;
}

export interface AcceptedFilterConfig {
  key: string;
  label: string;
  icon?: string;
  loadOption: (value: string | number) => Promise<FilterOption>;
}

export type CrudTableColumn<T> = TableColumn<T> & {
  icon?: string;
  avatar?: { src: string };
};

export interface DropdownAction<T = unknown> {
  label: string;
  icon: string;
  color?: string;
  onSelect: (item: T) => void;
}

export interface ComponentDetails {
  component: unknown;
  props?: Record<string, unknown>;
}

export interface CrudConfig<T = unknown> {
  endpoint: string;
  entityName: string;
  entityNamePlural: string;
  headerIcon?: string;
  headerHideTitle?: boolean;
  icon?: string;
  tableColumns?: CrudTableColumn<T>[];
  tableColumnsVisibility?: Record<string, boolean>;
  tableCopyId: boolean;
  customDropdownActions?: (item: T) => DropdownAction<T>[];
  useGrid?: boolean;
  itemLink?: (item: T) => string;
  onItemClick?: (item: T) => void;
  isItemClickable?: (item: T) => boolean;
  searchable: boolean;
  searchPlaceholder?: string;
  filters?: FilterConfig[];
  acceptedFilters?: AcceptedFilterConfig[];
  defaultFilters?: Record<string, string | number>;
  ordering?: Array<string | { id: string; label: string }>;
  defaultOrdering: string;
  pageSize?: number;
  pageSizeOptions?: number[];
  defaultBody?: Record<string, string | number>;
  formFields?: FormField[];
  formSchema?: z.ZodType;
  formFullscreen?: boolean;
  createFormFields?: FormField[];
  createFormSchema?: z.ZodType;
  createForm?: object;
  updateOnCreateModalOpen?: boolean;
  createLabel?: string;
  onCreation?: (data: Record<string, unknown>) => void;
  editFormFields?: FormField[];
  editFormSchema?: z.ZodType;
  editForm?: object;
  updateOnEditModalOpen?: boolean;
  putEndpoint?: (item: T) => string;
  modalIcon?: string | ((item: T) => string);
  modalIconClass?: string;
  modalAvatar?: (item: T) => Record<string, unknown>;
  deleteMessage?: (item: T) => ComponentDetails[];
  deleteEndpoint?: (item: T) => string;
  emptyMessage?: string;
  deleteVerb?: string;
  deleteIcon?: string;
  canRead: boolean;
  canCreate: boolean;
  canEdit: boolean | ((item: T) => boolean);
  canDelete: boolean | ((item: T) => boolean);
  showAccessDeniedError?: boolean;
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
