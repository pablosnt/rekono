<template>
  <MenuProfile>
    <v-container v-if="user" fluid>
      <v-row justify="center" dense>
        <v-col cols="8">
          <Mfa :user="user" @reload="getProfile()" />
        </v-col>
        <v-col cols="8">
          <PasswordChange />
        </v-col>
        <v-col cols="8">
          <ApiToken />
        </v-col>
      </v-row>
    </v-container>
  </MenuProfile>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const api = useApi("/api/profile", true);
const user = ref(null);
getProfile();
function getProfile(): void {
  api.get().then((response) => (user.value = response));
}
</script>
