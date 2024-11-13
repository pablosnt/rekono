<template>
  <v-card
    elevation="3"
    :title="data.name"
    :text="data.description"
    :prepend-avatar="data.icon"
    :hover="hover"
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
      <BaseLink :link="data.reference" />
    </template>
  </v-card>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  integration: Object,
  hover: { type: Boolean, required: false, default: false },
});
const data = ref(props.integration ? props.integration : {});
const alert = ref(useAlert());
</script>
