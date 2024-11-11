<template>
  <MenuAdministration>
    <v-container class="mt-5" fluid>
      <v-row justify="space-around" dense>
        <v-col align-self="center" cols="5">
          <NotificationShow
            v-if="smtp !== null"
            :api="smtpApi"
            :notification="smtp"
            title="Email"
            icon="mdi-email"
            loading-color="black"
            :form="NotificationSmtpForm"
          />
        </v-col>
        <v-col align-self="center" cols="5">
          <NotificationShow
            v-if="telegram != null"
            :api="telegramApi"
            :notification="telegram"
            title="Telegram"
            :subtitle="telegram?.bot ? `@${telegram?.bot}` : undefined"
            icon="mdi-send-circle mdi-rotate-315"
            icon-color="light-blue-accent-3"
            loading-color="primary"
            :link="
              telegram && telegram.is_available && telegram.bot
                ? `https://t.me/${telegram.bot}`
                : 'https://core.telegram.org/bots#how-do-i-create-a-bot'
            "
            :form="NotificationTelegramForm"
          >
            <template #prepend>
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
            </template>
          </NotificationShow>
        </v-col>
      </v-row>
    </v-container>
  </MenuAdministration>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const NotificationSmtpForm = resolveComponent("NotificationSmtpForm");
const smtpApi = useApi("/api/smtp/", true, "SMTP settings");
const smtp = ref(null);
smtpApi.get(1).then((response) => (smtp.value = response));

const NotificationTelegramForm = resolveComponent("NotificationTelegramForm");
const telegramApi = useApi(
  "/api/telegram/settings/",
  true,
  "Telegram settings",
);
const telegram = ref(null);
telegramApi.get(1).then((response) => (telegram.value = response));
</script>
