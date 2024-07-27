<template>
  <v-card title="Change Password" prepend-icon="mdi-key" variant="text">
    <template #append>
      <v-btn
        :icon="expand === null ? 'mdi-menu-down' : 'mdi-menu-up'"
        variant="plain"
        size="x-large"
        @click="expand = expand === null ? 'password' : null"
      />
    </template>
    <template #text>
      <v-expansion-panels v-model="expand">
        <v-expansion-panel value="password">
          <template #text>
            <v-container fluid>
              <v-text-field
                v-model="oldPassword"
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
              <FormPassword
                :api="api"
                submit-text="Change Password"
                :loading="loading"
                :old-password="oldPassword"
                icon="mdi-key-variant"
                @loading="(value) => (loading = value)"
                @completed="
                  alert('Password changed successfully', 'success');
                  expand = null;
                  oldPassword = null;
                "
                @error="
                  alert('Invalid old password', 'error');
                  oldPassword = null;
                "
              />
            </v-container>
          </template>
        </v-expansion-panel>
      </v-expansion-panels>
    </template>
  </v-card>
</template>

<script setup lang="ts">
const alert = useAlert();
const api = useApi("/api/profile/update-password/", true, "Password");
const oldPassword = ref(null);
const loading = ref(false);
const expand = ref(null);
const visible = ref(false);
</script>
