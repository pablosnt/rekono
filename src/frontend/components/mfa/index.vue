<template>
  <v-expansion-panel value="mfa">
    <v-expansion-panel-title
      disable-icon-rotate
      @click.prevent.stop="
        mfa = !mfa;
        registerMfa();
      "
    >
      <v-card-title class="text-h5">
        <v-icon icon="mdi-onepassword" color="red" />
      </v-card-title>
      <p class="text-h5">Multi Factor Authentication</p>
      <template #actions>
        <v-switch
          v-model="mfa"
          color="green"
          @update:model-value="registerMfa()"
        />
      </template>
    </v-expansion-panel-title>
    <v-expansion-panel-text>
      <v-container fluid>
        <v-row>
          <v-alert
            class="text-center"
            color="info"
            icon="$info"
            variant="tonal"
          >
            <template #text>
              <p v-if="!user.mfa">
                Scan this QR with an authenticator app (like
                <v-btn
                  class="pa-0 text-none mb-1"
                  density="compact"
                  text="Google Authenticator"
                  target="_blank"
                  href="https://support.google.com/accounts/answer/1066447"
                  variant="plain"
                />) and type a valid code to enable MFA in your account
              </p>
              <p v-if="user.mfa">
                {{
                  app
                    ? "Type a valid code from your authenticator app to disable MFA in your account"
                    : "Paste the token sent to your email to disable MFA in your account"
                }}
              </p>
            </template>
          </v-alert>
        </v-row>
        <v-row justify="center">
          <v-col>
            <UtilsQr
              v-if="!user.mfa && qrUrl"
              class="text-center"
              :data="qrUrl"
            />
            <MfaForm
              ref="mfaForm"
              :loading="loading"
              :allow-email="user.mfa"
              @new-otp="(mfa) => enableOrDisable(mfa)"
              @app="(value) => (app = value)"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup lang="ts">
const props = defineProps({ user: Object });
const emit = defineEmits(["reload", "collapse"]);
const alert = useAlert();
const api = useApi("/api/profile/mfa/", true);
const mfa = ref(props.user.mfa);
const mfaForm = ref(null);
const qrUrl = ref(null);
const loading = ref(false);
const app = ref(true);

function registerMfa(): void {
  if (mfa.value && props.user && !props.user.mfa) {
    api
      .create({}, undefined, "register/")
      .then((response) => (qrUrl.value = response.url))
      .catch(() => emit("collapse"));
  }
}

function enableOrDisable(otp: string): void {
  loading.value = true;
  let name = "enable";
  let alertType = "success";
  if (props.user.mfa) {
    name = "disable";
    alertType = "warning";
  }
  api
    .create({ mfa: otp }, undefined, `${name}/`)
    .then(() => {
      alert(`MFA has been ${name}d`, alertType);
      loading.value = false;
      emit("reload");
    })
    .catch((error) => {
      loading.value = false;
      mfaForm.value.clearOtp();
      if (error.statusCode === 401) {
        alert("Invalid OTP", "error");
      }
    });
}
</script>
