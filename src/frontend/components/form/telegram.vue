<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-container fluid>
      <v-row justify="center" dense>
        <v-text-field
          v-model="token"
          type="password"
          density="compact"
          label="Telegram token"
          prepend-icon="mdi-key"
          variant="outlined"
          :rules="[
            (t) =>
              !t || validate.secret.test(t.trim()) || 'Invalid Telegram token',
          ]"
          validate-on="input"
          clearable
          @update:model-value="disabled = false"
        />
      </v-row>
      <v-btn
        color="blue"
        size="large"
        variant="tonal"
        text="Save"
        type="submit"
        class="mt-5"
        :disabled="
          disabled || (token !== null && token === '*'.repeat(token.length))
        "
        block
        autofocus
      />
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  data: Object,
});
const emit = defineEmits(["completed", "loading"]);
const validate = ref(useValidation());
const valid = ref(true);
const disabled = ref(true);
const token = ref(props.data ? props.data.token : null);

function submit() {
  if (valid.value) {
    emit("loading", true);
    props.api
      .update({ token: token.value ? token.value.trim() : null }, 1)
      .then((response) => {
        emit("completed", response);
        emit("loading", false);
      });
  }
}
</script>
