<template>
  <MenuProfile>
    <v-container v-if="user" fluid>
      <v-row justify="center" dense>
        <v-col cols="7">
          <CardMfa :user="user" @reload="getProfile()" />
        </v-col>
        <v-col cols="7">
          <CardPassword />
        </v-col>
        <v-col cols="7">
          <CardTokens />
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
function getProfile() {
  api.get().then((response) => (user.value = response));
}
</script>
