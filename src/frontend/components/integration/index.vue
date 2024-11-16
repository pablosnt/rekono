<template>
  <v-card
    elevation="2"
    :title="data.name"
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
      <BaseButton :link="data.reference" new-tab hide />
    </template>
    <template #text>
      <p class="text-center">{{ data.description }}</p>
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
