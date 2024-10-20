<template>
  <v-container fluid>
    <v-row class="mt-3" justify="center" dense>
      <v-alert
        color="warning"
        icon="$warning"
        variant="tonal"
        :text="`Don't add sensitive information, like credentials, as part of a HTTP header because its value will be always shown on plain text. Use ${target ? 'scope' : 'target'} authentication instead`"
        closable
      />
    </v-row>
  </v-container>
  <Dataset
    ref="dataset"
    :api="api"
    :default-parameters="parameters"
    :add="HttpHeaderDialog"
    icon="mdi-web"
    empty-head="No HTTP Headers"
    :empty-text="`Custom HTTP headers will be sent by HTTP scanning tools that support this customization. ${!target && !user ? 'Note that these headers can be overwritten by each user or target' : !target ? 'Note that these headers can be overwritten by each target' : ''}`"
    @load-data="(data) => (headers = data)"
  >
    <template #data>
      <v-row dense>
        <v-col v-for="header in headers" :key="header.id" cols="6">
          <v-card elevation="3" class="mx-auto" density="compact">
            <HttpHeaderForm
              :api="api"
              :header="header"
              @completed="dataset.loadData(false)"
            />
          </v-card>
        </v-col>
      </v-row>
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
const headers = ref([]);
</script>
