<template>
  <CrudPage :config="config" />
</template>

<script setup lang="ts">
import { h, resolveComponent } from "vue";
import type { CrudConfig, FilterOption } from "~/types/crud";
import * as z from "zod";
import { useUserStore } from "~/store/user";
import type { Wordlist } from "~/types/models";

const userStore = useUserStore();
const validation = useValidation();
const backend = useBackend();
const api = useApi("/api/");
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
    options: backend.wordlistTypes,
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
  if (userStore.is_auditor) {
    backend.getUserOptions(userOptions, { role: "Admin" });
    backend.getUserOptions(userOptions, { role: "Auditor" });
  }
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
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("id")),
    },
    {
      accessorKey: "name",
      header: "Name",
      icon: "i-lucide-case-sensitive",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("name")),
    },
    {
      accessorKey: "type",
      header: "Type",
      icon: "i-lucide-tag",
      cell: ({ row }) => {
        const type = row.getValue("type");
        return h(resolveComponent("UBadge"), {
          color: "neutral",
          variant: "subtle",
          icon: backend.wordlistTypes.find((item) => item.value === type)?.icon,
          label: type,
        });
      },
    },
    {
      accessorKey: "size",
      header: "Words",
      icon: "i-lucide-file-text",
      cell: ({ row }) => {
        const size = row.getValue("size") as number;
        return h("span", { class: "font-medium" }, size?.toLocaleString());
      },
    },
    {
      accessorKey: "owner",
      header: "Owner",
      icon: "i-lucide-user",
      cell: ({ row }) => {
        const owner = row.getValue("owner") as Wordlist["owner"];
        return owner?.username ? `@${owner.username}` : "";
      },
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
        options: backend.wordlistTypes,
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
      ...(userStore.is_auditor
        ? [
            {
              key: "owner",
              label: "Owner",
              icon: "i-lucide-user",
              type: "select" as const,
              options: userOptions,
            },
          ]
        : [
            {
              key: "owner_username",
              label: "Owner",
              icon: "i-lucide-user",
              type: "text" as const,
              placeholder: "Filter by owner username...",
            },
          ]),
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
      type: z.enum(
        backend.wordlistTypes.map((t) => t.value) as [string, ...string[]],
      ),
      file: z
        .file("File is required")
        .max(maxMbSize.value * 1024 * 1024)
        .mime("text/plain"),
    });
  },
  editFormFields: formFields,
  editFormSchema: z.object({
    name: validation.name("name", true, 100),
    type: z.enum(
      backend.wordlistTypes.map((t) => t.value) as [string, ...string[]],
    ),
  }),
  deleteMessage: (wordlist: Wordlist) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this wordlist?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: wordlist.name,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
  ],
  canRead: userStore.is_auditor,
  canCreate: userStore.is_auditor,
  canEdit: (wordlist: Wordlist) =>
    userStore.is_admin || userStore.isOwner(wordlist, "owner"),
  canDelete: (wordlist: Wordlist) =>
    userStore.is_admin || userStore.isOwner(wordlist, "owner"),
});
</script>
