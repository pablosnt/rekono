<template>
  <UCollapsible v-model:open="open">
    <CrudPage
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
    </CrudPage>
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
            @complete="
              (value) => {
                userStore.profile.mfa
                  ? disable(value.join(''))
                  : enable(value.join(''));
              }
            "
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

function enable(otp: strig) {
  loading.value = true;
  api
    .create("enable/", { mfa: otp })
    .then((response) => {
      toast.add({
        description: "MFA has been enabled",
        color: "success",
      });
      userStore.updateProfile(response);
      open.value = false;
    })
    .finally(() => {
      loading.value = false;
      mailOtp.value = undefined;
      appOtp.value = undefined;
    });
}

function disable(otp: string) {
  loading.value = true;
  api
    .create("disable/", { mfa: otp })
    .then((response) => {
      toast.add({
        description: "MFA has been disabled",
        color: "warning",
      });
      userStore.updateProfile(response);
      open.value = false;
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
