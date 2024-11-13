<template>
  <UtilsNameDescriptionForm
    :edit="edit"
    @submit="(name, description) => submit(name, description)"
  >
    <BaseTagInput
      class="mt-2"
      :value="tags"
      @new-values="(value) => (tags = value)"
    />
  </UtilsNameDescriptionForm>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  edit: Object,
});
const emit = defineEmits(["completed", "loading"]);
const tags = ref(props.edit ? props.edit.tags : []);

function submit(name: string, description: string): void {
  emit("loading", true);
  const request = props.edit ? props.api.update : props.api.create;
  request(
    { name: name, description: description, tags: tags.value },
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
