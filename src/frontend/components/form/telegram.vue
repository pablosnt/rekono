<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-container fluid>
      <v-row justify="center" dense>
        <v-text-field
          v-model="telegram.token"
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
          telegram.token !== null &&
          telegram.token === '*'.repeat(telegram.token.length)
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
emit("loading", true);
const validate = ref(useValidation());
const valid = ref(true);

const telegram = ref({ token: null });
watch(
  () => props.data,
  () => {
    emit("loading", false);
    telegram.value = props.data;
  },
);

function submit() {
  if (valid.value) {
    emit("loading", true);
    props.api.update({ token: telegram.value.token }, 1).then((data) => {
      emit("completed", data);
      emit("loading", false);
    });
  }
}
</script>
