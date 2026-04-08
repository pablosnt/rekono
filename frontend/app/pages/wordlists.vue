<template>
  <CrudPage :config="config" />
</template>

<script setup lang="ts">
import { h, resolveComponent } from "vue";
import type { CrudConfig, FilterOption } from "~/types/crud";
import * as z from "zod";
import { useUserStore } from "~/store/user";
import type { Wordlist } from "~/types/models";
import { wordlistTypes } from "~/constants";

const userStore = useUserStore();
const validation = useValidation();
const options = useOptions();
const api = useApi("/api/");
const table = useTable();
const maxMbSize = ref(1);
const maxWordlistSize = ref(1000000);
const userOptions = ref<FilterOption[]>([]);
const formFields = [
  {
    key: "name",
    label: "Name",
    type: "text",
    required: true,
    placeholder: "Enter wordlist name",
  },
  {
    key: "type",
    label: "Type",
    type: "select",
    required: true,
    placeholder: "Select wordlist type",
    options: wordlistTypes,
    labelKey: "value",
  },
];

onMounted(() => {
  api.get("settings/1/").then((response) => {
    maxMbSize.value = response.max_uploaded_file_mb;
  });
  api
    .list("wordlists/", { ordering: "-size", size__gte: 0 }, false, 1, 1)
    .then((response) => {
      maxWordlistSize.value = response.items[0]?.size || maxWordlistSize.value;
    });
  options.users(userOptions, { role: "Admin", is_active: true });
  options.users(userOptions, { role: "Auditor", is_active: true });
});

const config: CrudConfig<Wordlist> = reactive({
  endpoint: "/api/wordlists/",
  entityName: "Wordlist",
  entityNamePlural: "Wordlists",
  icon: "i-mdi-file-word",
  tableColumns: [
    {
      accessorKey: "id",
      header: "ID",
      icon: "i-lucide-hash",
      cell: ({ row }) => table.valueCell(row.getValue("id")),
    },
    {
      accessorKey: "name",
      header: "Name",
      icon: "i-lucide-case-sensitive",
      cell: ({ row }) => table.valueCell(row.getValue("name")),
    },
    {
      accessorKey: "type",
      header: "Type",
      icon: "i-lucide-tag",
      cell: ({ row }) => {
        const type = row.getValue("type");
        return table.badgeCell(
          type,
          wordlistTypes.find((item) => item.value === type)?.icon,
        );
      },
    },
    {
      accessorKey: "size",
      header: "Words",
      icon: "i-lucide-file-text",
      cell: ({ row }) =>
        table.valueCell(row.getValue("size")?.toLocaleString()),
    },
    {
      accessorKey: "owner",
      header: "Owner",
      icon: "i-lucide-user",
      cell: ({ row }) => table.usernameCell(row.getValue("owner")),
    },
    {
      accessorKey: "likes",
      header: "Likes",
      icon: "i-lucide-thumbs-up",
      cell: ({ row }) => {
        const item = row.original as Wordlist;
        return h(resolveComponent("CrudLikes"), {
          itemId: item.id,
          endpoint: "/api/wordlists/",
          liked: item.liked,
          count: item.likes,
          onUpdate: (liked: boolean, count: number) => {
            item.liked = liked;
            item.likes = count;
          },
        });
      },
    },
  ],
  tableColumnsVisibility: {
    id: false,
    owner: false,
  },
  searchable: true,
  searchPlaceholder: "Search wordlists...",
  get filters() {
    return [
      {
        key: "type",
        label: "Type",
        icon: "i-lucide-tag",
        type: "select" as const,
        options: wordlistTypes,
        labelKey: "value",
      },
      {
        key: "size",
        label: "Words",
        icon: "i-lucide-file-text",
        type: "range" as const,
        min: 0,
        max: maxWordlistSize.value,
        step: 1000,
        multiple: true,
      },
      {
        key: "owner",
        label: "Owner",
        icon: "i-lucide-user",
        type: "select" as const,
        options: userOptions,
      },
      {
        key: "like",
        label: "Favourites",
        icon: "i-lucide-heart",
        type: "checkbox" as const,
      },
    ];
  },
  ordering: [
    "id",
    "name",
    "size",
    "type",
    "owner",
    { id: "likes_count", label: "Likes" },
  ],
  defaultOrdering: "-id",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  get createFormFields() {
    return [
      ...formFields,
      {
        key: "file",
        label: "File",
        type: "file",
        required: true,
        fileUploadLabel: "Upload wordlist file",
        fileUploadDescription: `Text file up to ${maxMbSize.value} MB`,
        accept: "text/plain",
        icon: "i-mdi-file-word",
      },
    ];
  },
  get createFormSchema() {
    return z.object({
      name: validation.name("name", true, 100),
      type: z.enum(wordlistTypes.map((t) => t.value) as [string, ...string[]]),
      file: z
        .file("File is required")
        .max(maxMbSize.value * 1024 * 1024)
        .mime("text/plain"),
    });
  },
  editFormFields: formFields,
  editFormSchema: z.object({
    name: validation.name("name", true, 100),
    type: z.enum(wordlistTypes.map((t) => t.value) as [string, ...string[]]),
  }),
  deleteMessage: (wordlist: Wordlist) =>
    buildDeleteMessage("wordlist", wordlist.name),
  canRead: userStore.is_auditor,
  canCreate: userStore.is_auditor,
  canEdit: (wordlist: Wordlist) =>
    userStore.is_admin || userStore.isOwner(wordlist),
  canDelete: (wordlist: Wordlist) =>
    userStore.is_admin || userStore.isOwner(wordlist),
});
</script>
