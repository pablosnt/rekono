<template>
  <v-container fluid>
    <v-row>
      <v-col class="text-center">
        <!-- todo: Use fixed-header option in other occurrences? -->
        <v-table v-if="portsShow.length > 0" density="compact">
          <thead>
            <tr>
              <th />
              <th class="text-center">Port</th>
              <th class="text-center">Service</th>
              <th class="text-center">Protocol</th>
              <th class="text-center">Status</th>
              <th />
            </tr>
          </thead>
          <tbody class="text-center">
            <tr v-for="port in portsShow" :key="port.id">
              <td><v-icon :icon="portsUtils.getIcon(port.port)" /></td>
              <td>{{ port.port }}</td>
              <td>{{ port.service }}</td>
              <td>{{ port.protocol }}</td>
              <td>
                <v-chip :color="enums.portStatus[port.status].color">{{
                  port.status
                }}</v-chip>
              </td>
              <td class="text-left">
                <UtilsCounter
                  icon="mdi-ladybug"
                  :collection="port.vulnerability"
                  :link="`/projects/${route.params.project_id}/findings?tab=vulnerabilities&host=${port.host}&port=${port.id}`"
                  tooltip="Vulnerabilities"
                  variant="text"
                />
                <v-btn
                  variant="text"
                  icon="mdi-arrow-right-circle"
                  color="medium-emphasis"
                  :to="`/projects/${route.params.project_id}/assets/${port.id}`"
                  hover
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
  ports: Array,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
defineEmits(["reload"]);
const route = useRoute();
const portsUtils = usePorts();
const enums = useEnums();
const maxPorts = 3;
const raw = props.ports
  .filter((p) => !p.auto_fixed)
  .sort((a, b) => a.port - b.port);
const show = ref(maxPorts < raw.length ? false : undefined);
const portsShow = computed(() => {
  return show.value ? raw : raw.slice(0, maxPorts);
});
</script>
