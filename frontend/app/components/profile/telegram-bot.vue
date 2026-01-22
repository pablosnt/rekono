<template>
  <CrudPage
    :config="{
      entityNamePlural: 'Telegram Bot',
      entityName: 'Telegram Bot',
      canRead: true,
      canEdit: false,
      canDelete: false,
      canCreate: false,
      showAccessDeniedError: false,
    }"
  >
    <template v-if="!userStore.profile?.telegram_chat" #header-actions>
      <UButton
        icon="i-lucide-external-link"
        variant="ghost"
        color="neutral"
        size="xl"
        :to="`https://t.me/${settings.bot}`"
        target="_blank"
        external
      />
    </template>
    <template #content>
      <template v-if="userStore.profile?.telegram_chat">
        <div class="flex justify-around">
          <UButton
            :label="`Go to @${settings.bot}`"
            icon="i-simple-icons-telegram"
            :to="`https://t.me/${settings.bot}`"
            target="_blank"
            color="info"
            size="xl"
          />
          <UButton
            :loading="loading"
            icon="i-lucide-unplug"
            color="error"
            label="Disconnect Telegram bot"
            size="xl"
            @click="
              () => {
                loading = true;
                api
                  .remove(`${userStore.profile.telegram_chat}/`)
                  .then(() => userStore.fetchProfile())
                  .finally(() => {
                    loading = false;
                  });
              }
            "
          />
        </div>
      </template>
      <template v-else>
        <UAlert
          class="mb-10"
          color="info"
          :description="`Go to @${settings.bot} and send the /start command`"
        >
          <template #description>
            <p>
              Go to
              <ULink
                class="font-bold"
                raw
                :to="`https://t.me/${settings.bot}`"
                target="_blank"
                >@{{ settings.bot }}</ULink
              >, send the
              <UBadge variant="subtle" color="neutral">/start</UBadge> command
              and paste here the token returned by the bot
            </p>
          </template>
        </UAlert>
        <CrudForm
          ref="form"
          :api="api"
          :config="config"
          @submit="userStore.fetchProfile()"
          @validation-change="(isValid) => (valid = isValid)"
          @new-loading="(newLoading) => (loading = newLoading)"
        />
        <UButton
          :disabled="!valid"
          :loading="loading"
          color="info"
          :label="`Log in @${settings.bot}`"
          block
          class="w-full mt-5"
          size="lg"
          icon="i-simple-icons-telegram"
          @click="
            loading = true;
            form.submit();
          "
        />
      </template>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import * as z from "zod";

const props = defineProps<{
  settings: Record<string, unknown>;
}>();

const api = useApi("/api/telegram/link/");
const validation = useValidation();
const userStore = useUserStore();
const loading = ref(false);
const valid = ref(false);
const form = ref();
const config = ref({
  entityName: "Telegram Bot",
  formFields: [
    {
      key: "otp",
      label: "Telegram token",
      type: "password",
      placeholder: `Paste the token provided by @${props.settings.bot}`,
      hint: `@${props.settings.bot}`,
      size: "xl",
      required: true,
      icon: "i-lucide-key",
    },
  ],
  formSchema: z.object({ otp: validation.secret("otp", true, 200) }),
});
</script>
