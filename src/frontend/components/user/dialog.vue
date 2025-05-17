<template>
  <BaseDialog
    title="Invite User"
    :loading="loading"
    @close-dialog="$emit('closeDialog')"
  >
    <v-form v-model="valid" @submit.prevent="submit()">
      <v-container fluid>
        <v-text-field
          v-model="email"
          class="mb-4"
          density="comfortable"
          label="Email"
          prepend-inner-icon="mdi-email"
          variant="outlined"
          :rules="[
            (e) => !!e || 'Email is required',
            (e) => validate.email.test(e) || 'Invalid email address',
          ]"
          validate-on="blur"
        />
        <BaseAutocomplete
          v-model="role"
          class="mb-8"
          label="Role"
          density="comfortable"
          variant="outlined"
          :definition="enums.roles"
          :rules="[(r) => !!r || 'Role is required']"
          validate-on="input"
          hide-details
        />
        <UtilsSubmit text="Invite" :autofocus="false" />
      </v-container>
    </v-form>
  </BaseDialog>
</template>

<script setup lang="ts">
const emit = defineEmits(["closeDialog", "completed"]);
const email = ref(null);
const role = ref("Reader");
const validate = useValidation();
const enums = useEnums();
const valid = ref(true);
const loading = ref(false);
const api = useApi("/api/users/", true, "User");

function submit(): void {
  if (valid.value) {
    loading.value = true;
    api
      .create({ email: email.value.trim(), role: role.value })
      .then((response) => {
        loading.value = false;
        emit("completed", response);
      })
      .catch(() => (loading.value = false));
  }
}
</script>
