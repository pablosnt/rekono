<template>
  <UCollapsible v-model:open="open" @animationend="onCollapseEnd">
    <CrudHeader
      :api="api"
      :config="{
        entityNamePlural: 'MFA',
        entityName: 'MFA',
        canRead: true,
        canEdit: false,
        canDelete: false,
        canCreate: false,
      }"
    >
      <template #header-leading>
        <USwitch
          :model-value="userStore.profile.mfa"
          :loading="loading"
          :aria-label="userStore.profile.mfa ? 'Disable MFA' : 'Enable MFA'"
          @change="(value) => handleSwitch(value)"
        />
      </template>
    </CrudHeader>
    <template #content>
      <template v-if="userStore.profile.mfa">
        <UAlert
          class="mb-5"
          icon="i-lucide-triangle-alert"
          color="warning"
          description="Input a valid OTP to disale your MFA. After that your account will be accessible with your credentials only"
        />
      </template>
      <template v-else>
        <UAlert
          class="mb-5"
          icon="i-lucide-info"
          color="info"
          description="Scan this QR code with your authenticator app and input a first valid OTP to enable your MFA"
        />
        <div class="flex items-center justify-center mb-5">
          <Qrcode
            v-if="url"
            class="w-64"
            variant="rounded"
            black-color="red"
            white-color="white"
            :radius="1"
            :value="url"
          />
          <USkeleton v-else class="size-64" />
        </div>
      </template>
      <template v-if="method === 'app'">
        <div class="flex items-center justify-center">
          <UPinInput
            v-model="appOtp"
            :length="6"
            highlight
            variant="outline"
            size="xl"
            color="neutral"
            aria-label="One-Time Password via app"
            @complete="(value) => switchEnableDisable(value.join(''))"
          />
        </div>
      </template>
      <template v-else>
        <UInput
          v-model="mailOtp"
          class="w-full"
          icon="i-lucide-key-square"
          size="xl"
          :maxlength="128"
          aria-label="One-Time Password via email"
          @update:model-value="
            () => {
              if (mailOtp?.length === 128) {
                disable(mailOtp);
              }
            }
          "
        >
          <template #trailing>
            <div
              class="text-xs text-muted tabular-nums"
              aria-live="polite"
              role="status"
            >
              {{ mailOtp?.length }}/128
            </div>
          </template>
        </UInput>
      </template>
      <div class="flex items-center justify-center">
        <UButton
          v-if="userStore.profile.mfa"
          :label="
            method === 'app'
              ? 'Disable via email OTP'
              : 'Disable via authenticator app'
          "
          color="neutral"
          variant="ghost"
          class="text-muted mt-3"
          @click="
            () => {
              method = method === 'app' ? 'email' : 'app';
              if (method === 'email') {
                emailApi.create('', {});
              }
            }
          "
        />
      </div>
    </template>
  </UCollapsible>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const api = useApi("/api/profile/mfa/");
const emailApi = useApi("/api/security/mfa/email/");
const toast = useToast();
const userStore = useUserStore();
const url = ref();
const method = ref("app");
const appOtp = ref();
const mailOtp = ref();
const loading = ref(false);
const open = ref(false);

const pendingProfile = ref();
function onCollapseEnd(event: AnimationEvent) {
  if (event.animationName === "collapsible-up" && pendingProfile.value) {
    userStore.updateProfile(pendingProfile.value);
    pendingProfile.value = undefined;
  }
}

function switchEnableDisable(otp: string) {
  loading.value = true;
  const word = userStore.profile.mfa ? "disable" : "enable";
  api
    .create(`${word}/`, { mfa: otp })
    .then((response) => {
      toast.add({
        description: `MFA has been ${word}d`,
        color: userStore.profile.mfa ? "success" : "warning",
      });
      open.value = false;
      pendingProfile.value = response;
    })
    .catch((error) => {
      if (error?.statusCode === 401) {
        toast.add({
          description: "Invalid MFA code. Please try again.",
          color: "error",
        });
      }
    })
    .finally(() => {
      loading.value = false;
      mailOtp.value = undefined;
      appOtp.value = undefined;
    });
}

function handleSwitch(value: boolean) {
  if (value && !userStore.profile.mfa) {
    api.create("register/", {}).then((response) => (url.value = response.url));
  }
}
</script>
