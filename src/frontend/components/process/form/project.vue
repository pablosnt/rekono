<template>
  <UtilsNameDescription
    :edit="edit"
    @submit="(name, description) => submit(name, description)"
  >
    <BaseTagInput
      class="mt-2"
      :value="tags"
      @input-value="(value) => (tag = value)"
      @new-values="(value) => (tags = value)"
    />
  </UtilsNameDescription>
</template>

<script setup lang="ts">
const props = defineProps({ api: Object, edit: Object });
const emit = defineEmits(["completed", "loading"]);
const tag = ref(null);
const tags = ref(props.edit ? props.edit.tags : []);

function submit(name: string, description: string): void {
  emit("loading", true);
  const request = props.edit ? props.api.update : props.api.create;
  request(
    {
      name: name,
      description: description,
      tags: tag.value === null ? tags.value : tags.value.concat(tag.value),
    },
    props.edit?.id,
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
