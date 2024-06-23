<template>
  <v-card
    elevation="4"
    :title="data.name"
    :text="data.description"
    :prepend-avatar="data.icon"
    :hover="data.id === 1 || data.id === 4"
  >
    <template #append>
      <v-switch
        :model-value="data.enabled"
        color="success"
        class="mt-5"
        @click.stop="
          api.update({ enabled: !data.enabled }, data.id).then((response) => {
            data = response;
            data.enabled
              ? alert(`${data.name} integration has been enabled`, 'success')
              : alert(`${data.name} integration has been disabled`, 'warning');
          })
        "
      />
      <ButtonLink :link="data.reference" />
    </template>
  </v-card>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  integration: Object,
});
const data = ref(props.integration ? props.integration : {});
const alert = ref(useAlert());
</script>
