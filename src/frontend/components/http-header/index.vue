<template>
  <Dataset
    ref="dataset"
    :api="api"
    :default-parameters="parameters"
    :add="HttpHeaderDialog"
    icon="mdi-web"
    empty-head="No HTTP Headers"
    empty-text="Create the HTTP headers that must be sent by HTTP hacking tools"
    auditor
  >
    <template #prepend-search>
      <v-row class="mb-5" dense>
        <v-alert
          class="text-center"
          color="warning"
          icon="$warning"
          variant="tonal"
          :text="`Don't add sensitive information, like credentials, as part of a HTTP header because its value will be always shown on plain text. Use ${target ? 'scope' : 'target'} authentication instead`"
          closable
        />
      </v-row>
    </template>
    <template #item="{ item }">
      <v-card elevation="1" class="ma-5">
        <HttpHeaderForm
          class="ml-4 mt-6"
          :api="api"
          :header="item"
          @completed="dataset.loadData(false)"
        />
      </v-card>
    </template>
  </Dataset>
</template>

<script setup lang="ts">
const props = defineProps({
  target: {
    type: Number,
    required: false,
    default: null,
  },
  user: {
    type: Number,
    required: false,
    default: null,
  },
});
const parameters = ref(
  Object.assign(
    { ordering: "id" },
    props.target ? { target: props.target } : { target__isnull: true },
    props.user ? { user: props.user } : { user__isnull: true },
  ),
);
const HttpHeaderDialog = resolveComponent("HttpHeaderDialog");
const api = ref(useApi("/api/http-headers/", true, "HTTP header"));
const dataset = ref(null);
</script>
