<template>
  <v-card title="API Tokens" prepend-icon="mdi-api" variant="text">
    <template #append>
      <v-dialog width="auto">
        <template #activator="{ props: activatorProps }">
          <v-btn
            icon="mdi-plus-thick"
            variant="text"
            size="large"
            color="green"
            v-bind="activatorProps"
          />
        </template>
        <template #default="{ isActive }">
          <ApiTokenDialog
            :api="api"
            @completed="dataset.loadData(false)"
            @close-dialog="isActive.value = false"
          />
        </template>
      </v-dialog>
    </template>
    <template #text>
      <Dataset
        ref="dataset"
        :api="api"
        ordering="-expiration"
        :header="false"
        icon="mdi-api"
        empty-head="No API Tokens"
        empty-text="There are no API tokens"
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
                <td class="text-center">
                  {{ new Date(token.expiration).toDateString() }}
                </td>
                <td>
                  <UtilsButtonDelete
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
    </template>
  </v-card>
</template>

<script setup lang="ts">
const api = useApi("/api/api-tokens/", true, "API token");
const tokens = ref([]);
const dataset = ref(null);
</script>
