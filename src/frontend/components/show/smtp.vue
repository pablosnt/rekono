<template>
  <v-card title="e-Mail" class="mx-auto" elevation="4" color="grey-lighten-3">
    <template #prepend>
      <v-icon size="x-large" icon="mdi-email" />
    </template>
    <template #append>
      <ButtonGreenCheck
        v-if="!loading"
        :condition="smtp?.is_available"
        true-text="Available"
        false-text="Not available"
      />
      <v-progress-circular
        v-if="loading"
        class="ma-3"
        color="black"
        :size="24"
        indeterminate
      />
    </template>
    <v-card-text>
      <FormSmtp
        :api="api"
        :data="smtp"
        @completed="(data) => (smtp = data)"
        @loading="(value) => (loading = value)"
      />
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
const loading = ref(false);
const api = useApi("/api/smtp/", true, "SMTP settings");
const smtp = ref({
  host: null,
  port: null,
  tls: false,
  username: null,
  password: null,
});
api.get(1).then((data) => (smtp.value = data));
</script>
