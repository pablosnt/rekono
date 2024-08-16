<template>
  <DialogDefault
    title="Invite User"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <v-form v-model="valid" @submit.prevent="submit()">
      <v-conatiner fluid>
        <v-text-field
          v-model="email"
          class="mt-3"
          density="comfortable"
          label="Email"
          prepend-inner-icon="mdi-email"
          variant="outlined"
          :rules="[
            (e) => !!e || 'Email is required',
            (e) => validate.email.test(e) || 'Invalid Email address',
          ]"
          validate-on="blur"
        />
        <v-autocomplete
          v-model="role"
          auto-select-first
          density="comfortable"
          variant="outlined"
          :prepend-inner-icon="role ? enums.roles[role].icon : undefined"
          :color="role ? enums.roles[role].color : undefined"
          label="Role"
          :items="Object.keys(enums.roles)"
          :rules="[(r) => !!r || 'Role is required']"
          validate-on="input"
          hide-details
        />

        <ButtonSubmit text="Invite" :autofocus="false" class="mt-5" />
      </v-conatiner>
    </v-form>
  </DialogDefault>
</template>

<script setup lang="ts">
const emit = defineEmits(["closeDialog", "completed"]);
const email = ref(null);
const role = ref(null);
const validate = ref(useValidation());
const enums = ref(useEnums());
const valid = ref(true);
const loading = ref(false);
const api = useApi("/api/users/", true, "User");

function submit() {
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
