<template>
  <v-text-field
    v-model="newTag"
    :label="label"
    :persistent-placeholder="tags.length > 0"
    :prepend-inner-icon="icon"
    variant="outlined"
    :rules="[(t) => !t || regex.test(t.trim()) || 'Invalid value']"
    validate-on="input"
    @update:model-value="
      (value) =>
        $emit(
          'inputValue',
          value && regex.test(value.trim()) ? value.trim() : null,
        )
    "
  >
    <template #append-inner>
      <BaseButton
        icon="mdi-plus-thick"
        color="green"
        :disabled="
          !newTag ||
          !newTag.trim() ||
          !regex.test(newTag.trim()) ||
          tags.includes(newTag.trim())
        "
        @click="
          tags.push(newTag.trim());
          $emit('newValues', tags);
          $emit('newValue', newTag);
          newTag = null;
        "
      />
    </template>
    <v-chip-group class="justify-center" multiple>
      <v-chip
        v-for="tag in tags"
        :key="tag"
        :text="tag"
        closable
        @click:close="
          tags.splice(tags.indexOf(tag), 1);
          $emit('newValues', tags);
          $emit('removeValue', tag);
        "
      />
    </v-chip-group>
  </v-text-field>
</template>

<script setup lang="ts">
const props = defineProps({
  value: { type: Array, required: false, default: null },
  label: { type: String, required: false, default: "Tags" },
  icon: { type: String, required: false, default: "mdi-tag" },
  validate: { type: RegExp, required: false, default: null },
});
defineEmits(["newValue", "newValues", "inputValue", "removeValue"]);
const regex = props.validate === null ? useValidation().name : props.validate;
const newTag = ref(null);
const tags = ref(props.value != null ? props.value : []);

function addTag(tag: string): void {
  tags.value.push(tag.trim());
}

function removeTag(tag: string): void {
  tags.value.splice(tags.value.indexOf(tag.trim()), 1);
}

defineExpose({ addTag, removeTag });
</script>
