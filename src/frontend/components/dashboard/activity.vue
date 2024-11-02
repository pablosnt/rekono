<template>
  <DashboardWindow
    title="Recent activity"
    icon="mdi-history"
    :project="project"
    :target="target"
  >
    <v-container v-if="stats" fluid>
      <v-row justify="space-around">
        <v-col v-if="!project && !target" cols="4">
          <v-card title="Top Projects" prepend-icon="mdi-folder-open">
            <template #text>
              <v-table density="comfortable">
                <tbody>
                  <tr v-for="project in stats.top_projects" :key="project.id">
                    <td class="text-center text-capitalize">
                      {{ project.name }}
                    </td>
                    <td><TagShow :item="project" /></td>
                    <td class="text-center">
                      <UtilsCounter
                        :collection="project.targets"
                        tooltip="Targets"
                        icon="mdi-target"
                        :link="`/projects/${project.id}/targets`"
                      />
                      <UtilsButtonLink
                        :link="`/projects/${project.id}/`"
                        target="_self"
                        icon="mdi-arrow-right-circle"
                      />
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </template>
            <v-card-actions>
              <v-btn
                variant="outlined"
                to="/projects"
                block
                text="All projects"
              />
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col>
          <v-card title="Latest Scans" prepend-icon="mdi-play-network">
            <template #text>
              <v-table density="comfortable">
                <tbody>
                  <tr v-for="task in stats.latest_tasks" :key="task.id">
                    <td class="text-right">
                      <v-avatar
                        v-if="task.configuration && task.configuration.icon"
                        :image="task.configuration.icon"
                      />
                      <v-icon
                        v-if="task.process"
                        icon="mdi-robot-angry"
                        color="red"
                      />
                      <v-icon
                        v-if="task.configuration && !task.configuration.icon"
                        icon="mdi-rocket"
                        color="red"
                      />
                    </td>
                    <td class="text-center text-capitalize">
                      {{
                        task.process
                          ? task.process.name
                          : task.configuration.tool.name
                      }}
                    </td>
                    <td class="text-center text-capitalize">
                      <p v-if="task.configuration">
                        {{ task.configuration.name }}
                      </p>
                    </td>
                    <td class="text-center">
                      <v-progress-circular
                        v-if="task.status && task.status === 'Running'"
                        :model-value="task.progress"
                        size="45"
                        width="5"
                        color="amber"
                      >
                        <template #default>{{ task.progress }}%</template>
                      </v-progress-circular>
                      <v-chip
                        v-if="task.status && task.status !== 'Running'"
                        :color="enums.statuses[task.status].color"
                      >
                        <v-icon
                          :icon="enums.statuses[task.status].icon"
                          start
                        />
                        {{ task.status }}
                      </v-chip>
                    </td>

                    <td class="text-center">
                      <v-chip
                        color="red"
                        :to="`/projects/${task.target.project}/targets/${task.target.id}`"
                        target="_blank"
                        @click.stop
                      >
                        <v-icon icon="mdi-target" start />
                        {{ task.target.target }}
                      </v-chip>
                    </td>
                    <td class="text-right">
                      <UtilsButtonLink
                        :link="`/projects/${task.target.project}/scans/${task.id}`"
                        target="_self"
                        icon="mdi-arrow-right-circle"
                      />
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </template>
          </v-card>
        </v-col>
      </v-row>
      <v-row class="mt-10" justify="space-around">
        <v-col>
          <v-card
            title="Latest Assets"
            :prepend-icon="enums.findings.Host.icon"
            color="indigo-lighten-2"
            density="comfortable"
          >
            <template #text>
              <v-table density="comfortable">
                <tbody>
                  <tr v-for="host in stats.latest_hosts" :key="host.id">
                    <td class="text-right">
                      <v-btn icon variant="text">
                        <v-icon
                          :icon="enums.osType[host.os_type].icon"
                          :color="enums.osType[host.os_type].color"
                        />
                        <v-tooltip activator="parent" :text="host.os_type" />
                      </v-btn>
                    </td>
                    <td class="text-center text-capitalize">
                      {{ host.address }}
                    </td>
                    <td class="text-center">
                      <FindingToolCounter :finding="host" />
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </template>
          </v-card>
        </v-col>
        <v-col>
          <v-card
            title="Latest Vulnerabilities"
            :prepend-icon="enums.findings.Vulnerability.icon"
            color="red-lighten-2"
            density="comfortable"
          >
            <template #text>
              <v-table density="comfortable">
                <tbody>
                  <tr
                    v-for="vulnerability in stats.latest_vulnerabilities"
                    :key="vulnerability.id"
                  >
                    <td class="text-right">
                      <v-btn icon variant="text">
                        <v-icon
                          :icon="enums.severity[vulnerability.severity].icon"
                          :color="enums.severity[vulnerability.severity].color"
                        />
                        <v-tooltip
                          activator="parent"
                          :text="vulnerability.severity"
                        />
                      </v-btn>
                    </td>
                    <td class="text-center text-capitalize">
                      {{
                        vulnerability.cve
                          ? vulnerability.cve
                          : vulnerability.name
                      }}
                    </td>
                    <td class="text-center">
                      <v-btn v-if="vulnerability.trending" icon variant="text">
                        <v-icon icon="mdi-fire" color="orange" size="x-large" />
                        <v-tooltip activator="parent" text="Trending CVE" />
                      </v-btn>
                      <v-chip
                        v-if="vulnerability.cwe"
                        :href="`https://cwe.mitre.org/data/definitions/${vulnerability.cwe.toLowerCase().split('-')[1]}.html`"
                        target="_blank"
                        :text="vulnerability.cwe.toUpperCase()"
                        @click.stop
                      />
                      <FindingExploitDialog
                        v-if="vulnerability.exploit.length > 0"
                        :vulnerability="vulnerability"
                      />
                    </td>

                    <td class="text-center">
                      <FindingToolCounter :finding="vulnerability" />
                    </td>

                    <td class="text-right">
                      <UtilsButtonLink :link="vulnerability.reference" />
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </DashboardWindow>
</template>

<script setup lang="ts">
const props = defineProps({
  project: {
    type: Object,
    required: false,
    default: null,
  },
  target: {
    type: Object,
    required: false,
    default: null,
  },
});
const enums = useEnums();
const api = useApi("/api/stats/activity/", true);
const stats = ref(null);

api
  .get(
    null,
    props.project || props.target
      ? `?${props.target ? props.target.id : props.project.id}`
      : null,
  )
  .then((response) => {
    stats.value = response;
    if (
      !props.project &&
      !props.target &&
      (!response.top_projects || response.top_projects.length === 0)
    ) {
      navigateTo("/projects");
    }
  });
</script>
