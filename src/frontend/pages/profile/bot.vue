<template>
  <MenuProfile>
    <v-container fluid>
      <v-row justify="center" dense>
        <v-col cols="8">
          <v-card
            :loading="loading ? 'blue' : false"
            variant="text"
            class="mt-5"
            width="100%"
          >
            <template #title>
              <v-card-title class="text-h5">
                <v-icon
                  size="x-large"
                  icon="mdi-send-circle mdi-rotate-315"
                  color="light-blue-accent-3"
                />
                <span class="me-1" />
                Rekono Bot
              </v-card-title>
            </template>
            <template
              v-if="
                user &&
                user.telegram_chat === null &&
                telegram &&
                telegram.is_available
              "
              #append
            >
              <BaseButton :link="`https://t.me/${telegram.bot}`" new-tab />
            </template>
            <template #text>
              <v-container
                v-if="user && telegram && !telegram?.is_available"
                fluid
              >
                <v-row dense>
                  <v-col>
                    <v-alert
                      v-if="user.role === 'Admin'"
                      color="warning"
                      icon="$warning"
                      variant="tonal"
                    >
                      <template #text>
                        <p>
                          Telegram integration is not configured yet, so Rekono
                          Bot can't be used. You can configure and enable the
                          integration in the
                          <v-btn
                            class="pa-0 text-none font-weight-bold"
                            density="compact"
                            text="Administration page"
                            variant="plain"
                            to="/administration/notifications"
                          />
                        </p>
                      </template>
                    </v-alert>
                    <v-alert
                      v-if="user.role !== 'Admin'"
                      color="warning"
                      icon="$warning"
                      variant="tonal"
                      text="Telegram integration is not configured yet, so Rekono Bot can't be used. Ask your administrator to enable it, they can do it in the Notifications section on the Administration page"
                    />
                  </v-col>
                </v-row>
              </v-container>
              <v-container
                v-if="
                  user &&
                  telegram &&
                  telegram?.is_available &&
                  user?.telegram_chat !== null
                "
                fluid
              >
                <v-row dense>
                  <v-col>
                    <v-btn
                      color="blue"
                      size="x-large"
                      variant="tonal"
                      prepend-icon="mdi-robot"
                      append-icon="mdi-send-circle mdi-rotate-315"
                      text="Take me to the Rekono Bot!"
                      class="mt-5"
                      block
                      autofocus
                      target="_blank"
                      :href="`https://t.me/${telegram.bot}`"
                    />
                  </v-col>
                </v-row>
                <v-row class="mt-5" dense>
                  <v-col>
                    <v-btn
                      prepend-icon="mdi-logout-variant"
                      variant="tonal"
                      text="Logout Rekono Bot"
                      color="red-lighten-2"
                      block
                      @click="unlink()"
                    />
                  </v-col>
                </v-row>
              </v-container>
              <v-container
                v-if="
                  user &&
                  telegram &&
                  telegram?.is_available &&
                  user?.telegram_chat === null
                "
                fluid
              >
                <v-row dense>
                  <v-col>
                    <v-alert color="info" icon="$info" variant="tonal">
                      <template #text>
                        <p class="text-center">
                          Go to the
                          <v-btn
                            class="pa-0 text-none font-weight-bold"
                            density="compact"
                            :text="`@${telegram.bot}`"
                            variant="plain"
                            target="_blank"
                            :href="`https://t.me/${telegram.bot}`"
                          />
                          and run the command
                          <span class="font-weight-bold font-italic"
                            >/start</span
                          >. Then paste here the token
                          <v-btn
                            class="pa-0 text-none font-weight-bold"
                            density="compact"
                            :text="`@${telegram.bot}`"
                            variant="plain"
                            target="_blank"
                            :href="`https://t.me/${telegram.bot}`"
                          />
                          sent you to link your account with your chat
                        </p>
                      </template>
                    </v-alert>
                  </v-col>
                </v-row>
                <v-form v-model="valid" class="mt-5" @submit.prevent="link()">
                  <v-row dense>
                    <v-col>
                      <v-text-field
                        v-model="token"
                        type="password"
                        density="comfortable"
                        label="Token"
                        prepend-inner-icon="mdi-key"
                        variant="outlined"
                        :rules="[
                          (t) => !!t || 'Token is required',
                          (t) => t.length === 128 || 'Invalid token',
                        ]"
                        validate-on="input"
                        clearable
                        @update:model-value="disabled = false"
                      />
                    </v-col>
                  </v-row>
                  <v-row dense>
                    <v-col>
                      <UtilsSubmit
                        text="Link Rekono Bot"
                        class="mt-5"
                        :disabled="disabled"
                      />
                    </v-col>
                  </v-row>
                </v-form>
              </v-container>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </MenuProfile>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const alert = useAlert();

const telegram = ref(null);
useApi("/api/telegram/settings/", true)
  .get(1)
  .then((response) => (telegram.value = response));

const user = ref(null);
getProfile();

const api = useApi("/api/telegram/link/", true);
const token = ref(null);
const valid = ref(true);
const disabled = ref(true);
const loading = ref(false);

function getProfile(): void {
  useApi("/api/profile/", true)
    .get()
    .then((response) => (user.value = response));
}

function link(): void {
  if (valid.value) {
    loading.value = true;
    api
      .create({ otp: token.value })
      .then(() => {
        getProfile();
        alert("Rekono Bot has been linked to your account", "success");
        loading.value = false;
      })
      .catch((error) => {
        loading.value = false;
        if (error.statusCode === 401) {
          alert("Invalid Rekono Bot token", "error");
        }
      });
  }
}

function unlink(): void {
  loading.value = true;
  api
    .remove(user.value.telegram_chat)
    .then(() => {
      getProfile();
      alert("Your user session has been closed in Rekono Bot", "warning");
      loading.value = false;
    })
    .catch(() => (loading.value = false));
}
</script>
