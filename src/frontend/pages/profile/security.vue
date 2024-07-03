<template>
  <MenuProfile>
    <v-container v-if="user" fluid>
      <v-row justify="center" dense>
        <v-col cols="7">
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
              <v-expansion-panels v-model="expandMfa">
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
                            :loading="disableMfaLoading"
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
        </v-col>
        <v-col cols="7">
          <v-card title="Change Password" prepend-icon="mdi-key" variant="text">
            <template #append>
              <v-btn
                :icon="
                  expandPassword === null ? 'mdi-menu-down' : 'mdi-menu-up'
                "
                variant="plain"
                size="x-large"
                @click="
                  expandPassword = expandPassword === null ? 'password' : null
                "
              />
            </template>
            <template #text>
              <v-expansion-panels v-model="expandPassword">
                <v-expansion-panel value="password" />
              </v-expansion-panels>
            </template>
          </v-card>
        </v-col>
        <v-col cols="7">
          <v-card title="API Tokens" prepend-icon="mdi-api" variant="text">
            <template #append>
              <!-- Put here the plus button and hide header in the dataset integration -->
            </template>
            <template #text />
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </MenuProfile>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });

const mfaApi = useApi("/api/profile/mfa/", true);
const passwordApi = useApi("/api/profile/update-password/", true, "Password");
const tokensApi = useApi("/api/api-tokens/", true, "API token");
const profileApi = useApi("/api/profile", true);
const alert = useAlert();

const expandMfa = ref(null);
const expandPassword = ref(null);

const mfa = ref(false);
const qrUrl = ref(null);
const enableMfaForm = ref(null);
const enableMfaLoading = ref(false);
const disableMfaForm = ref(null);
const disableMfaLoading = ref(false);

const user = ref(null);
getProfile();

function getProfile() {
  profileApi.get().then((response) => {
    user.value = response;
    mfa.value = user.value.mfa;
  });
}

function mfaSection() {
  expandMfa.value = expandMfa.value === null ? "mfa" : null;
  if (mfa.value && !user.value.mfa) {
    mfaApi
      .create({}, undefined, "register/")
      .then((response) => (qrUrl.value = response.url))
      .catch(() => (expandMfa.value = null));
  }
}

function enableMfa(otp) {
  enableMfaLoading.value = true;
  mfaApi
    .create({ mfa: otp }, undefined, "enable/")
    .then(() => {
      alert("MFA has been enabled", "success");
      getProfile();
      expandMfa.value = null;
      enableMfaLoading.value = false;
    })
    .catch((error) => {
      enableMfaLoading.value = false;
      enableMfaForm.value.clearOtp();
      if (error.statusCode === 401) {
        alert("Invalid OTP", "error");
      }
    });
}

function disableMfa(otp) {
  disableMfaLoading.value = true;
  mfaApi
    .create({ mfa: otp }, undefined, "disable/")
    .then(() => {
      alert("MFA has been disabled", "warning");
      getProfile();
      expandMfa.value = null;
      disableMfaLoading.value = false;
    })
    .catch((error) => {
      disableMfaLoading.value = false;
      disableMfaForm.value.clearOtp();
      if (error.statusCode === 401) {
        alert("Invalid OTP", "error");
      }
    });
}
</script>
