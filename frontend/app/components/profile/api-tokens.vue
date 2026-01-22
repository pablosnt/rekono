<template>
  <CrudPage :config="apiTokensConfig" />
</template>

<script setup lang="ts">
import * as z from "zod";

const apiTokensConfig = ref({
  endpoint: "/api/api-tokens/",
  entityNamePlural: "API tokens",
  entityName: "API token",
  icon: "", // TODO
  tableColumns: [], // TODO
  tableColumnsVisibility: {}, // TODO
  ordering: [], // TODO
  defaultOrdering: "-id",
  pageSize: 5,
  pageSizeOptions: [5, 25, 50, 100],
  formFields: [
    // TODO: name, expiration
  ],
  formSchema: z.object({}), // TODO
  // createForm: TODO
  // deleteMessage: TODO
  canRead: true,
  canEdit: false,
  canDelete: true,
  canCreate: true,
  showAccessDeniedError: false,
});
</script>
