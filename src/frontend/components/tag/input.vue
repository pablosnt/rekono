<template>
  <v-text-field
    v-model="newTag"
    :label="tags.length === 0 ? label : undefined"
    :prepend-inner-icon="icon"
    variant="outlined"
    :rules="[(t) => !t || regex.test(t.trim()) || 'Invalid value']"
    validate-on="input"
    @update:model-value="
      newTag !== null && regex.test(newTag.trim())
        ? $emit('newValue', newTag.trim())
        : $emit('newValue', null)
    "
  >
    <template #append-inner>
      <v-btn
        icon="mdi-plus-thick"
        color="green"
        variant="text"
        :disabled="
          !newTag ||
          !newTag.trim() ||
          !regex.test(newTag.trim()) ||
          tags.includes(newTag.trim())
        "
        @click="
          tags.push(newTag.trim());
          $emit('newValues', tags);
          newTag = null;
          $emit('newValue', newTag);
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
        "
      />
    </v-chip-group>
  </v-text-field>
</template>

<script setup lang="ts">
const props = defineProps({
  value: {
    type: Array,
    required: false,
    default: null,
  },
  label: {
    type: String,
    required: false,
    default: "Tags",
  },
  icon: {
    type: String,
    required: false,
    default: "mdi-tag",
  },
  validate: {
    type: RegExp,
    required: false,
    default: null,
  },
});
defineEmits(["newValue", "newValues"]);
const regex = props.validate === null ? useValidation().name : props.validate;
const newTag = ref(null);
const tags = ref(props.value != null ? props.value : []);
</script>
