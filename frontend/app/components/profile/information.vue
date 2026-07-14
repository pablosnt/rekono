<template>
  <CrudPage
    :config="{
      entityNamePlural: 'Profile',
      entityName: 'Profile',
      canRead: true,
      canEdit: true,
      canDelete: false,
      canCreate: false,
    }"
  >
    <template #content>
      <UProgress :class="[loading ? 'visible' : 'invisible', 'mb-1']" />
      <CrudForm
        ref="form"
        :api="api"
        :config="config"
        :entity="profile"
        @submit="
          (data) => {
            notifyEmailChange(data.email);
            profile = data;
            userStore.updateProfile(data);
            valid = false;
          }
        "
        @validation-change="(isValid) => (valid = isValid)"
        @new-loading="(newLoading) => (loading = newLoading)"
      />
      <div class="mt-8 flex justify-end">
        <UButton
          :disabled="!valid"
          :loading="loading"
          label="Save"
          @click="
            loading = true;
            form.submit();
          "
        />
      </div>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";
import * as z from "zod";

const api = useApi("/api/profile/");
const toast = useToast();
const userStore = useUserStore();
const integrations = useIntegrationsStore();
const validation = useValidation();
const form = ref();
const profile = ref(userStore.profile);
const loading = ref(false);
const valid = ref(false);
const notificationScopes = ["Only alerts", "Only my executions", "All executions"];
const config = computed(() => ({
  entityName: "Profile",
  editFormFields: [
    {
      key: "username",
      label: "Username",
      type: "text",
      placeholder: "Enter your username",
      required: true,
      disabled: true,
      icon: "i-lucide-at-sign",
    },
    {
      key: "email",
      label: "Email",
      type: "text",
      placeholder: "Enter your email address",
      required: true,
      icon: "i-lucide-mail",
      help: "Changing your email sends a verification link to the new address. Your current email stays active until you confirm it.",
    },
    {
      key: "first_name",
      label: "First name",
      type: "text",
      placeholder: "Enter your first name",
      required: false,
    },
    {
      key: "last_name",
      label: "Last name",
      type: "text",
      placeholder: "Enter your last name",
      required: false,
    },
    {
      key: "notification_scope",
      label: "Notifications scope",
      type: "select",
      required: true,
      options: notificationScopes,
      icon: "i-lucide-bell-ring",
      hidden:
        integrations.smtp?.is_available !== true &&
        integrations.telegram?.is_available !== true,
    },
    {
      key: "email_notifications",
      label: "Email notifications",
      type: "checkbox",
      required: true,
      hidden: integrations.smtp?.is_available !== true,
    },
    {
      key: "telegram_notifications",
      label: "Telegram notifications",
      type: "checkbox",
      required: true,
      hidden: integrations.telegram?.is_available !== true,
    },
  ],
  editFormSchema: z.object({
    username: validation.name("username", true, 100),
    first_name: validation.name("first_name", false, 100).or(z.literal("")),
    last_name: validation.name("last_name", false, 100).or(z.literal("")),
    email: validation.email,
    notification_scope: z.enum(notificationScopes),
    email_notifications: z.boolean(),
    telegram_notifications: z.boolean(),
  }),
  putEndpoint: () => "/api/profile/",
}));


function notifyEmailChange(savedEmail: string) {
  const requestedEmail = form.value?.formData?.email;
  if (!requestedEmail || requestedEmail === savedEmail) return;
  toast.add({
    title: "Confirm your new email address",
    description: `A verification link has been sent to ${requestedEmail}. Confirm it to get your email updated, ${savedEmail} stays active meanwhile`,
    color: "info",
    icon: "i-lucide-mail-check",
  });
}

onMounted(() => {
  integrations.fetchSmtp();
  integrations.fetchTelegram();
});
</script>
