<template></template>

<!-- TODO:
    Vulnerability (per Port or Technology) (new page)
      -- Exploits (Dialog)

    Check all findings have the relationships needed on creation
    -->

    <script setup lang="ts">
defineProps({
  api: Object,
  findings: Array,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
});
defineEmits(["reload"]);
const enums = useEnums();
</script>