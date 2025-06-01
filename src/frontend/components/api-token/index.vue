<template>
  <v-expansion-panel ref="panel" value="api-tokens">
    <v-expansion-panel-title disable-icon-rotate>
      <v-card-title class="text-h5">
        <v-icon icon="mdi-api" color="red" />
      </v-card-title>
      <p class="text-h5">API Tokens</p>
      <template #actions>
        <BaseButton
          class="mt-1"
          icon="mdi-xml"
          link="/api/schema/swagger-ui.html"
          color="red"
          new-tab
          @click="$emit('expand', panel ? panel.value : null)"
        />
        <v-dialog width="auto">
          <template #activator="{ props: activatorProps }">
            <BaseButton
              icon="mdi-plus-thick"
              size="large"
              color="green"
              v-bind="activatorProps"
              @click="$emit('expand', panel ? panel.value : null)"
            />
          </template>
          <template #default="{ isActive }">
            <ApiTokenDialog
              :api="api"
              @completed="
                dataset.loadData(false);
                $emit('expand', panel ? panel.value : null);
              "
              @close-dialog="
                isActive.value = false;
                $emit('expand', panel ? panel.value : null);
              "
            />
          </template>
        </v-dialog>
      </template>
    </v-expansion-panel-title>
    <v-expansion-panel-text>
      <Dataset
        ref="dataset"
        :api="api"
        :default-parameters="{ id: '-expiration' }"
        :header="false"
        icon="mdi-api"
        empty-head="No API Tokens"
        empty-text="Create your first API token to make API requests"
        @load-data="(data) => (tokens = data)"
      >
        <template #data>
          <v-table density="compact">
            <thead>
              <tr>
                <th class="text-center font-weight-bold">Name</th>
                <th class="text-center font-weight-bold">Expiration</th>
                <th />
              </tr>
            </thead>
            <tbody>
              <tr v-for="token in tokens" :key="token.id">
                <td class="text-center text-capitalize">{{ token.name }}</td>
                <td
                  :class="`text-center ${new Date(token.expiration) <= new Date() ? 'text-red' : ''}`"
                >
                  {{ new Date(token.expiration).toDateString() }}
                </td>
                <td>
                  <UtilsDeleteButton
                    :id="token.id"
                    :api="api"
                    :text="`API token '${token.name}' will be removed`"
                    @completed="dataset.loadData(false)"
                  />
                </td>
              </tr>
            </tbody>
          </v-table>
        </template>
      </Dataset>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup lang="ts">
defineEmits(["expand"]);
const api = useApi("/api/api-tokens/", true, "API token");
const tokens = ref([]);
const dataset = ref(null);
const panel = ref(null);
</script>
