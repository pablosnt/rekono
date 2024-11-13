<template>
  <BaseDialog
    :title="data.name"
    :avatar="data.icon"
    :loading="!color ? loading : false"
    @close-dialog="$emit('closeDialog')"
  >
    <template #append>
      <UtilsGreenCheck
        v-if="!loading"
        :condition="isAvailable"
        true-text="Available"
        false-text="Not Available"
      />
      <v-progress-circular
        v-if="loading"
        class="ma-3"
        :color="color"
        :size="24"
        indeterminate
      />
      <span class="me-3" />
      <v-switch
        :model-value="data.enabled"
        color="success"
        class="mt-5"
        @click="
          api.update({ enabled: !data.enabled }, data.id).then((response) => {
            data = response;
            data.enabled
              ? alert(`${data.name} integration has been enabled`, 'success')
              : alert(`${data.name} integration has been disabled`, 'warning');
          })
        "
      />
      <span class="me-3" />
      <BaseLink :link="data.reference" />
    </template>
    <template #default>
      <slot />
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  integration: Object,
  isAvailable: Boolean,
  color: String,
  loading: Boolean,
});
const data = ref(props.integration ? props.integration : {});
const alert = ref(useAlert());
defineEmits(["closeDialog"]);
</script>
