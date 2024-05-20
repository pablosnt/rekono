<template>
  <MenuAdministration>
    <v-container class="mt-5" fluid>
      <v-row justify="space-around" dense>
        <v-col align-self="center" cols="5">
          <ShowSmtp />
        </v-col>
        <v-col align-self="center" cols="5">
          <ShowTelegram />
        </v-col>
      </v-row>
    </v-container>
  </MenuAdministration>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
</script>
