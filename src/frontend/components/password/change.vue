<template>
  <v-expansion-panel value="password">
    <v-expansion-panel-title>
      <v-card-title class="text-h5">
        <v-icon icon="mdi-key-change" color="red" />
      </v-card-title>
      <p class="text-h5">Change Password</p>
    </v-expansion-panel-title>
    <v-expansion-panel-text>
      <v-container fluid>
        <PasswordForm
          v-model="password"
          icon="mdi-key-variant"
          submit-text="Change Password"
          :submit-disabled="loading || !oldPassword"
          @custom-submit="(valid) => submit(valid)"
        >
          <template #prepend>
            <v-text-field
              v-model="oldPassword"
              class="mb-2"
              :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
              :type="visible ? 'text' : 'password'"
              density="comfortable"
              label="Old password"
              prepend-inner-icon="mdi-key"
              variant="outlined"
              :rules="[(p) => !!p || 'Password is required']"
              validate-on="blur"
              @click:append-inner="visible = !visible"
            />
          </template>
        </PasswordForm>
      </v-container>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup lang="ts">
const emit = defineEmits(["collapse"]);
const alert = useAlert();
const api = useApi("/api/profile/update-password/", true, "Password");
const password = ref(null);
const oldPassword = ref(null);
const loading = ref(false);
const visible = ref(false);

function submit(valid: boolean): void {
  if (valid && oldPassword.value) {
    loading.value = true;
    api
      .update({ password: password.value, old_password: oldPassword.value })
      .then(() => {
        loading.value = false;
        password.value = null;
        oldPassword.value = null;
        alert("Password changed successfully 1", "success");
        emit("collapse");
        oldPassword.value = null;
      })
      .catch(() => {
        loading.value = false;
        alert("Invalid old password", "error");
        oldPassword.value = null;
      });
  }
}
</script>
