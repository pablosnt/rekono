<template>
  <MenuProfile>
    <v-container v-if="user" fluid>
      <v-row justify="center">
        <v-expansion-panels v-model="expand" variant="accordion">
          <v-col cols="8">
            <Mfa
              :user="user"
              @reload="
                getProfile();
                expand = null;
              "
              @collapse="expand = null"
            />
          </v-col>
          <v-col cols="8">
            <PasswordChange @collapse="expand = null" />
          </v-col>
          <v-col cols="8">
            <ApiToken @expand="(value) => (expand = value)" />
          </v-col>
        </v-expansion-panels>
      </v-row>
    </v-container>
  </MenuProfile>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const api = useApi("/api/profile", true);
const expand = ref(null);
const user = ref(null);
getProfile();
function getProfile(): void {
  api.get().then((response) => (user.value = response));
}
</script>
