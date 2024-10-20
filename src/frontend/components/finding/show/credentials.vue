<template>
  <v-container fluid>
    <v-row>
      <v-col class="text-center">
        <v-table v-if="credentialsShow.length > 0" density="compact">
          <thead>
            <tr>
              <th />
              <th class="text-center">Email</th>
              <th class="text-center">Username</th>
              <th class="text-center">Secret</th>
              <th />
            </tr>
          </thead>
          <tbody class="text-center">
            <tr v-for="credential in credentialsShow" :key="credential.id">
              <td>
                <v-btn v-if="credential.context !== null" variant="text" icon>
                  <v-icon color="info" icon="$info" />
                  <v-tooltip activator="parent" :text="credential.context" />
                </v-btn>
              </td>
              <td>{{ credential.email }}</td>
              <td>{{ credential.username }}</td>
              <td>{{ credential.secret }}</td>
              <td class="text-left">
                <FindingFix
                  :api="api"
                  :finding="credential"
                  @change="$emit('reload')"
                />
                <NoteButton
                  :project="route.params.project_id"
                  :credential="credential"
                />
                <FindingLinks
                  :finding="credential"
                  :defectdojo="defectdojo"
                  :defectdojo-settings="defectdojoSettings"
                  :hacktricks="hacktricks"
                />
              </td>
            </tr>
          </tbody>
        </v-table>
        <v-btn
          v-if="show !== undefined"
          :text="show ? 'SHOW LESS' : 'SHOW MORE'"
          variant="plain"
          @click="show = !show"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
const props = defineProps({
  credentials: Array,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
defineEmits(["reload"]);
const route = useRoute();
const api = useApi("/api/credentials/", true);
const max = 3;
const raw = props.credentials.filter((p) => !p.auto_fixed);
const show = ref(max < raw.length ? false : undefined);
const credentialsShow = computed(() => {
  return show.value ? raw : raw.slice(0, max);
});
</script>
