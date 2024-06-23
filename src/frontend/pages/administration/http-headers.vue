<template>
  <MenuAdministration>
    <v-container fluid>
      <v-row justify="center" dense>
        <v-alert
          color="info"
          icon="$info"
          variant="tonal"
          text="Custom HTTP headers might be needed to scan some targets. They will be sent by HTTP scanning tools that support this customization. Note that these headers can be overwritten by each user or target"
          closable
        />
      </v-row>
      <v-row class="mt-3" justify="center" dense>
        <v-alert
          color="warning"
          icon="$warning"
          variant="tonal"
          text="Don't add sensitive information, like credentials, as part of a HTTP header because its value will be always shown on plain text. Please, configure authentication per target instead"
          closable
        />
      </v-row>
    </v-container>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="[]"
      :default-parameters="{ target__isnull: true, user__isnull: true }"
      ordering="id"
      :add="DialogHttpHeader"
      icon="mdi-web"
      empty="There are no default HTTP headers"
      @load-data="(data) => (headers = data)"
    >
      <template #data>
        <v-row dense>
          <v-col v-for="header in headers" :key="header.id" cols="6">
            <v-card elevation="4" class="mx-auto" density="compact">
              <v-card-text>
                <FormHttpHeader
                  :api="api"
                  :header="header"
                  @completed="dataset.loadData(false)"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </Dataset>
  </MenuAdministration>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
defineEmits(["closeDialog"]);
const DialogHttpHeader = resolveComponent("DialogHttpHeader");
const api = ref(useApi("/api/http-headers/", true, "HTTP header"));
const dataset = ref(null);
const headers = ref([]);
</script>
