<template>
  <MenuAdministration>
    <v-container class="mt-5" fluid>
      <v-row justify="space-around" dense>
        <v-col align-self="center" cols="5">
          <Notification
            v-if="smtp !== null"
            :api="smtpApi"
            :notification="smtp"
            title="Email"
            :form="NotificationFormSmtp"
          />
        </v-col>
        <v-col align-self="center" cols="5">
          <Notification
            v-if="telegram !== null"
            :api="telegramApi"
            :notification="telegram"
            title="Telegram"
            :subtitle="telegram?.bot ? `@${telegram?.bot}` : undefined"
            :link="
              telegram && telegram.is_available && telegram.bot
                ? `https://t.me/${telegram.bot}`
                : 'https://core.telegram.org/bots#how-do-i-create-a-bot'
            "
            :form="NotificationFormTelegram"
            @completed="(data) => (telegram = data)"
          />
        </v-col>
      </v-row>
    </v-container>
  </MenuAdministration>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const NotificationFormSmtp = resolveComponent("NotificationFormSmtp");
const NotificationFormTelegram = resolveComponent("NotificationFormTelegram");
const smtpApi = useApi("/api/smtp/", true, "SMTP settings");
const telegramApi = useApi(
  "/api/telegram/settings/",
  true,
  "Telegram settings",
);
const smtp = ref(null);
const telegram = ref(null);
smtpApi.get(1).then((response) => (smtp.value = response));
telegramApi.get(1).then((response) => (telegram.value = response));
</script>
