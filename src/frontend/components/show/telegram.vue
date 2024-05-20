<template>
  <v-card
    title="Telegram"
    :subtitle="telegram?.bot ? `@${telegram?.bot}` : undefined"
    class="mx-auto"
    elevation="4"
    color="light-blue-lighten-5"
  >
    <template #prepend>
      <v-icon
        size="x-large"
        color="light-blue-accent-3"
        icon="mdi-send-circle mdi-rotate-315"
      />
    </template>
    <template #append>
      <ButtonGreenCheck
        v-if="!loading"
        :condition="telegram?.is_available"
        true-text="Available"
        false-text="Not available"
      />
      <v-progress-circular
        v-if="loading"
        class="mr-3"
        color="primary"
        :size="24"
        indeterminate
      />
      <v-btn
        variant="text"
        icon="mdi-open-in-new"
        color="medium-emphasis"
        target="_blank"
        :href="
          telegram && telegram.is_available && telegram.bot
            ? `https://t.me/${telegram.bot}`
            : 'https://core.telegram.org/bots#how-do-i-create-a-bot'
        "
        hover
      />
    </template>
    <v-card-text>
      <v-alert
        v-if="!telegram || !telegram.is_available || !telegram.bot"
        color="info"
        icon="$info"
        variant="outline"
      >
        <template #text>
          Register your bot by messaging
          <v-btn
            class="pa-0 text-none font-weight-bold"
            density="compact"
            text="@BotFather"
            target="_blank"
            href="https://t.me/botfather"
            variant="plain"
          />
          and set up your authentication token here
        </template>
      </v-alert>
      <FormTelegram
        :api="api"
        :data="telegram"
        @completed="(data) => (telegram = data)"
        @loading="(value) => (loading = value)"
      />
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
const loading = ref(false);
const api = useApi("/api/telegram/settings/", true, "Telegram settings");
const telegram = ref({ bot: null, token: null });
api.get(1).then((data) => (telegram.value = data));
</script>
