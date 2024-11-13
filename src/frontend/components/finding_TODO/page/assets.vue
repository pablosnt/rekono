<template>
  <Dataset
    v-if="filtering.length > 0"
    ref="dataset"
    :api="api"
    :icon="enums.findings.Host.icon"
    :filtering="filtering"
    :default-parameters="defaultParameters"
    empty-head="No assets found"
    empty-text="Run some enumeration tool to identify some assets exposed by your targets"
    @load-data="
      (data) => {
        forceReload++;
      }
    "
  >
    <template #item="{ item }">
      <FindingShowHost
        :key="forceReload > 1 ? forceReload : 1"
        :api="api"
        :finding="item"
        :defectdojo="defectdojo"
        :defectdojo-settings="defectdojoSettings"
        :hacktricks="hacktricks"
        @reload="dataset.loadData(false)"
      />
    </template>
  </Dataset>
</template>

<script setup lang="ts">
const props = defineProps({
  defaultParameters: Object,
  globalFiltering: Array,
  triageFiltering: Array,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
  matchQuery: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const enums = useEnums();
const filters = useFilters();
const api = useApi("/api/hosts/", true);
const dataset = ref(null);
const forceReload = ref(0);
const filtering = ref([]);
filters
  .build([
    {
      cols: 2,
      type: "autocomplete",
      label: "OS",
      icon: enums.osType.Other.icon,
      collection: filters.collectionFromEnum(enums.osType),
      fieldValue: "name",
      fieldTitle: "name",
      key: "os_type",
    },
  ])
  .then((hostFilters) => {
    filters
      .build([
        {
          type: "autocomplete",
          label: "Sort",
          icon: "mdi-sort",
          cols: 2,
          collection: ["id", "host", "address", "os_type"],
          fieldValue: "id",
          fieldTitle: "name",
          key: "ordering",
          defaultValue: "-id",
        },
      ])
      .then((orderFilters) => {
        filtering.value = hostFilters
          .concat(props.globalFiltering)
          .concat(orderFilters);
      });
  });
</script>
