<template>
  <v-card
    title="Multi Factor Authentication"
    prepend-icon="mdi-onepassword"
    variant="text"
    subtitle="Authenticator App"
  >
    <template #append>
      <v-switch
        v-model="mfa"
        color="green"
        @update:model-value="mfaSection()"
      />
    </template>
    <template #text>
      <v-expansion-panels v-model="expand">
        <v-expansion-panel value="mfa">
          <template #text>
            <v-container fluid>
              <v-row dense>
                <v-alert
                  v-if="!user.mfa"
                  class="text-center"
                  color="info"
                  icon="$info"
                  variant="tonal"
                  text="Scan this QR with an Authenticator app and type a valid code to enable MFA in your account"
                />
                <v-alert
                  v-if="user.mfa"
                  class="text-center"
                  color="info"
                  icon="$info"
                  variant="tonal"
                  text="Type a valid code to disable MFA in your account"
                />
              </v-row>
              <v-row justify="center" dense>
                <v-col v-if="!user.mfa && qrUrl">
                  <ShowQr class="text-center" :data="qrUrl" />
                  <FormMfa
                    ref="enableMfaForm"
                    :loading="enableMfaLoading"
                    :auto-trigger="true"
                    @new-otp="(mfa) => enableMfa(mfa)"
                  />
                </v-col>
                <v-col v-if="user.mfa">
                  <FormMfa
                    ref="disableMfaForm"
                    :loading="loading"
                    :allow-email="true"
                    :auto-trigger="true"
                    @new-otp="(mfa) => disableMfa(mfa)"
                  />
                </v-col>
              </v-row>
            </v-container>
          </template>
        </v-expansion-panel>
      </v-expansion-panels>
    </template>
  </v-card>
</template>

<script setup lang="ts">
const alert = useAlert();
const emit = defineEmits(["reload"]);
const props = defineProps({ user: Object });
const api = useApi("/api/profile/mfa/", true);
const mfa = ref(false);
const qrUrl = ref(null);
const enableForm = ref(null);
const disableForm = ref(null);
const loading = ref(false);
const expand = ref(null);

function mfaSection() {
  expand.value = expand.value === null ? "mfa" : null;
  if (mfa.value && props.user && !props.user.mfa) {
    api
      .create({}, undefined, "register/")
      .then((response) => (qrUrl.value = response.url))
      .catch(() => (expand.value = null));
  }
}
function enableOrDisable(otp, name, alert, form) {
  loading.value = true;
  api
    .create({ mfa: otp }, undefined, `${name}/`)
    .then(() => {
      alert(`MFA has been ${name}d`, alert);
      emit("reload");
      expand.value = null;
      loading.value = false;
    })
    .catch((error) => {
      loading.value = false;
      form.clearOtp();
      if (error.statusCode === 401) {
        alert("Invalid OTP", "error");
      }
    });
}
function enableMfa(otp) {
  enableOrDisable(otp, "enable", "success", enableForm.value);
}
function disableMfa(otp) {
  enableOrDisable(otp, "disable", "warning", disableForm.value);
}
</script>
