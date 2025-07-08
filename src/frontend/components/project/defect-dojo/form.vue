<template>
  <UtilsNameDescription
    :disabled="disabled"
    @submit="(name, description) => submit(name, description)"
  />
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  disabled: { type: Boolean, required: false, default: false },
  extraData: { type: Object, required: false, default: null },
});
const emit = defineEmits(["completed", "loading"]);

function submit(name: string, description: string): void {
  emit("loading", true);
  props.api
    .create(
      Object.assign(
        {},
        { name: name, description: description },
        props.extraData !== null ? props.extraData : {},
      ),
    )
    .then((response) => {
      emit("completed", response);
      emit("loading", false);
    })
    .catch(() => {
      emit("loading", false);
    });
}
</script>
