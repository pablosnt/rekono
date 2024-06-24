<template>
  <v-container fluid>
    <v-row justify="center" dense>
      <v-alert
        color="info"
        icon="$info"
        variant="tonal"
        :text="`Custom HTTP headers will be sent by HTTP scanning tools that support this customization. ${!target && !user ? 'Note that these headers can be overwritten by each user or target' : !target ? 'Note that these headers can be overwritten by each target' : ''}`"
        closable
      />
    </v-row>
    <v-row class="mt-3" justify="center" dense>
      <v-alert
        color="warning"
        icon="$warning"
        variant="tonal"
        text="Don't add sensitive information, like credentials, as part of a HTTP header because its value will be always shown on plain text. Use target authentication instead"
        closable
      />
    </v-row>
  </v-container>
  <Dataset
    ref="dataset"
    :api="api"
    :filtering="[]"
    :default-parameters="parameters"
    ordering="id"
    :add="DialogHttpHeader"
    icon="mdi-web"
    empty="There are no custom HTTP headers"
    @load-data="(data) => (headers = data)"
  >
    <template #data>
      <v-row dense>
        <v-col v-for="header in headers" :key="header.id" cols="6">
          <v-card elevation="4" class="mx-auto" density="compact">
            <FormHttpHeader
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
    {},
    props.target ? { target: props.target } : { target__isnull: true },
    props.user ? { user: props.user } : { user__isnull: true },
  ),
);
const DialogHttpHeader = resolveComponent("DialogHttpHeader");
const api = ref(useApi("/api/http-headers/", true, "HTTP header"));
const dataset = ref(null);
const headers = ref([]);
</script>
