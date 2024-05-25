<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-container fluid>
      <v-row justify="center" dense>
        <v-text-field
          v-model="target"
          :disabled="pattern && pattern.default"
          variant="outlined"
          label="Target Pattern"
          prepend-icon="mdi-network-off"
          clearable
          validate-on="input"
          :rules="[
            (t) => !!t || 'Target pattern is required',
            (t) =>
              validate.targetRegex.test(t.trim()) || 'Invalid target pattern',
          ]"
          @update:model-value="disabled = false"
        >
          <template v-if="pattern && !pattern.default" #append>
            <ButtonSave
              v-if="!pattern.default"
              :disabled="disabled"
              @click="submit"
            />
            <ButtonDelete
              v-if="!pattern.default"
              :id="pattern.id"
              :api="api"
              :text="`Target pattern '${pattern.target}' will be removed`"
              @completed="$emit('completed')"
            />
            <v-chip v-if="pattern.default" text="Default" />
          </template>
        </v-text-field>
      </v-row>
      <v-btn
        v-if="!pattern"
        color="red"
        size="large"
        variant="tonal"
        text="Create"
        type="submit"
        class="mt-5"
        block
        autofocus
        :disabled="disabled"
      />
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  pattern: {
    type: Object,
    required: false,
    default: null,
  },
});
const emit = defineEmits(["completed", "loading"]);
const validate = useValidation();

const valid = ref(true);
const disabled = ref(props.pattern !== null);
const target = ref(props.pattern ? props.pattern.target : null);

function submit() {
  if (valid.value) {
    let request = null;
    const body = { target: target.value.trim() };
    if (props.pattern) {
      request = props.api.update(body, props.pattern.id);
    } else {
      request = props.api.create(body);
    }
    request
      .then(() => {
        disabled.value = true;
        emit("loading", false);
        emit("completed");
      })
      .catch(() => emit("loading", false));
  }
}
</script>
