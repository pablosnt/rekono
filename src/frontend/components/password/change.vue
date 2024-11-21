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
        <v-text-field
          v-model="oldPassword"
          class="mb-2"
          :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
          :type="visible ? 'text' : 'password'"
          density="compact"
          label="Old password"
          prepend-inner-icon="mdi-key"
          variant="outlined"
          :rules="[(p) => !!p || 'Password is required']"
          validate-on="blur"
          @click:append-inner="visible = !visible"
        />
        <PasswordForm
          :api="api"
          submit-text="Change Password"
          :loading="loading"
          :old-password="oldPassword"
          icon="mdi-key-variant"
          @loading="(value) => (loading = value)"
          @completed="
            alert('Password changed successfully', 'success');
            $emit('collapse');
            oldPassword = null;
          "
          @error="
            alert('Invalid old password', 'error');
            oldPassword = null;
          "
        />
      </v-container>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup lang="ts">
defineEmits(["collapse"]);
const alert = useAlert();
const api = useApi("/api/profile/update-password/", true, "Password");
const oldPassword = ref(null);
const loading = ref(false);
const visible = ref(false);
</script>
