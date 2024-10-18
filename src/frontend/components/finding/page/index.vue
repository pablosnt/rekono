<template>
  <component
    v-if="globalFiltering.length > 0 && (!triage || triageFiltering.length > 0)"
    :is="page"
    :default-parameters="defaultParameters"
    :global-filtering="globalFiltering"
    :triage-filtering="triageFiltering"
    :defectdojo="defectdojo"
    :defectdojo-settings="defectdojoSettings"
    :hacktricks="hacktricks"
    :match-query="matchQuery"
  />
</template>

<script setup lang="ts">
const props = defineProps({
  page: Object,
  task: {
    type: Object,
    required: false,
    default: null,
  },
  execution: {
    type: Object,
    required: false,
    default: null,
  },
  matchQuery: {
    type: Boolean,
    required: false,
    default: false,
  },
  triage: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const user = userStore();
const enums = useEnums();
const route = useRoute();
const filters = useFilters();

const defaultParameters = ref(
  props.execution
    ? { executions: [props.execution.id] }
    : props.task
      ? { task: props.task.id }
      : route.params.task_id
        ? { task: route.params.task_id }
        : { project: route.params.project_id },
);

const hacktricks = ref(null);
const defectdojo = ref(null);
const defectdojoSettings = ref(null);
const integrationApi = useApi("/api/integrations/", true);
integrationApi.get(3).then((response) => (hacktricks.value = response));
integrationApi.get(1).then((response) => (defectdojo.value = response));
useApi("/api/defect-dojo/settings/", true)
  .get(1)
  .then((response) => (defectdojoSettings.value = response));

let globalFiltering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      cols: 2,
      label: "Target",
      icon: "mdi-target",
      request: useApi("/api/targets/", true).list(
        { project: route.params.project_id, ordering: "target" },
        true,
      ),
      fieldValue: "id",
      fieldTitle: "target",
      key: "target",
      skip: props.execution !== null || route.params.task_id,
      callback: (value, definitions) => {
        const task = filters.getDefinitionFromKey("task", definitions);
        const host = filters.getDefinitionFromKey("host", definitions);
        if (value) {
          task.disabled = false;
          useApi("/api/tasks/", true)
            .list(
              {
                project: route.params.project_id,
                target: value,
                ordering: "-id",
              },
              true,
            )
            .then((response) => {
              task.collection = response.items;
              filters.setValueFromQuery(task)
            });
          if (host) {
            useApi("/api/hosts/", true)
              .list(
                {
                  project: route.params.project_id,
                  target: value,
                  ordering: "address",
                },
                true,
              )
              .then((response) => { host.collection = response.items; filters.setValueFromQuery(host) });
          }
        } else {
          task.disabled = true;
          task.value = null;
          task.collection = [];
          if (host) {
            host.request.then((response) => { host.collection = response.items; filters.setValueFromQuery(host) });
          }
        }
      },
    },
    {
      type: "autocomplete",
      cols: 3,
      label: "Scan",
      icon: "mdi-play-network",
      collection: [],
      fieldValue: "id",
      key: "task",
      skip: props.execution !== null || route.params.task_id,
      disabled: true,
    },
    {
      type: "autocomplete",
      cols: 2,
      label: "Tool",
      icon: "mdi-rocket",
      enforceIcon: true,
      request: useApi("/api/tools/", true).list({ ordering: "name" }, true),
      fieldValue: "id",
      fieldTitle: "name",
      key: "tool",
      skip: props.execution !== null,
    },
    {
      type: "switch",
      label: "Fixed",
      color: "green",
      cols: 1,
      key: "is_fixed",
      trueValue: true,
      falseValue: false,
      defaultValue: false,
      callback: (value, definitions) => {
        const auto = filters.getDefinitionFromKey("auto_fixed", definitions);
        const mine = filters.getDefinitionFromKey("fixed_by", definitions);
        auto.disabled = value === false;
        mine.disabled = value === false;
        if (!value) {
          auto.value = null;
          mine.value = null;
        }
      },
    },
    {
      type: "switch",
      label: "Auto Fixed",
      color: "green",
      cols: 1,
      key: "auto_fixed",
      trueValue: true,
      falseValue: null,
      disabled: true,
      callback: (value, definitions) => {
        const mine = filters.getDefinitionFromKey("fixed_by", definitions);
        mine.disabled = value !== null;
        if (mine.disabled) {
          mine.value = null;
        }
      },
    },
    {
      type: "switch",
      label: "My Fixes",
      color: "blue",
      cols: 1,
      key: "fixed_by",
      trueValue: user.user,
      falseValue: null,
      isAuditor: true,
      disabled: true,
      callback: (value, definitions) => {
        const mine = filters.getDefinitionFromKey("auto_fixed", definitions);
        mine.disabled = value !== null;
        if (mine.disabled) {
          mine.value = null;
        }
      },
    },
  ])
  .then((result) => {
    globalFiltering.value = result;
  });

const triageFiltering = ref([]);
if (props.triage) {
  filters
    .build([
      {
        cols: 3,
        type: "autocomplete",
        label: "Triage Status",
        icon: enums.triage.Untriaged.icon,
        collection: filters.collectionFromEnum(enums.triage),
        fieldValue: "name",
        fieldTitle: "name",
        key: "triage_status__in",
        defaultValue: ["Untriaged", "True Positive", "Won't Fix"],
        multiple: true,
      },
      {
        type: "switch",
        label: "My Triage",
        color: "blue",
        cols: 1,
        key: "triage_by",
        trueValue: user.user,
        falseValue: null,
        isAuditor: true,
      },
    ])
    .then((result) => (triageFiltering.value = result));
}
</script>
