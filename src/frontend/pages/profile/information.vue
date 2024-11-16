<template>
  <MenuProfile>
    <v-container fluid>
      <v-row dense>
        <v-col>
          <v-card
            v-if="user"
            variant="text"
            :title="`@${user.username}`"
            :subtitle="user.email"
          >
            <template #prepend>
              <v-avatar variant="outlined">
                <v-icon
                  :icon="enums.roles[user.role].icon"
                  :color="enums.roles[user.role].color"
                  size="x-large"
                />
              </v-avatar>
            </template>
            <template #append>
              <p class="text-medium-emphasis">
                Joined on {{ new Date(user.date_joined).toDateString() }}
              </p>
            </template>
            <template #text>
              <v-form v-model="valid" @submit.prevent="submit()">
                <v-container fluid>
                  <v-row justify="center" dense>
                    <v-col cols="4">
                      <v-text-field
                        v-model="user.first_name"
                        prepend-icon="mdi-card-account-details"
                        label="Name"
                        variant="outlined"
                        :rules="[
                          (n) =>
                            !n ||
                            validate.name.test(n.trim()) ||
                            'Invalid name',
                        ]"
                        validate-on="input"
                        clearable
                        @update:model-value="disabled = false"
                      />
                    </v-col>
                    <v-col cols="4">
                      <v-text-field
                        v-model="user.last_name"
                        label="Last name"
                        variant="outlined"
                        :rules="[
                          (n) =>
                            !n ||
                            validate.name.test(n.trim()) ||
                            'Invalid last name',
                        ]"
                        validate-on="input"
                        clearable
                        @update:model-value="disabled = false"
                      />
                    </v-col>
                  </v-row>
                  <v-row justify="center" dense>
                    <v-col cols="8">
                      <v-card
                        title="Notifications"
                        prepend-icon="mdi-bell-ring"
                        variant="outlined"
                      >
                        <template #text>
                          <v-row>
                            <v-col>
                              <v-autocomplete
                                v-model="user.notification_scope"
                                auto-select-first
                                density="comfortable"
                                variant="outlined"
                                label="Scope"
                                :items="enums.notificationScopes"
                                :rules="[(s) => !!s || 'Scope is required']"
                                validate-on="input"
                                hide-details
                                @update:model-value="disabled = false"
                              />
                            </v-col>
                            <v-col>
                              <v-autocomplete
                                v-model="platforms"
                                multiple
                                auto-select-first
                                density="comfortable"
                                variant="outlined"
                                label="Platforms"
                                :items="
                                  Object.keys(enums.notificationPlatforms)
                                "
                                :disabled="
                                  user.notification_scope === 'Disabled'
                                "
                                hide-details
                                clearable
                                @update:model-value="disabled = false"
                              />
                            </v-col>
                          </v-row>
                        </template>
                      </v-card>
                    </v-col>
                  </v-row>
                  <v-row class="mt-5" justify="center" dense>
                    <v-col cols="8">
                      <UtilsSubmit text="Save" :disabled="disabled" />
                    </v-col>
                  </v-row>
                </v-container>
              </v-form>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </MenuProfile>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const enums = useEnums();
const validate = useValidation();
const user = ref(null);
const platforms = ref([]);
const valid = ref(true);
const disabled = ref(true);
const api = useApi("/api/profile/", true, "Profile");
api.get().then((response) => {
  user.value = response;
  getPlatforms();
});

function getPlatforms(): void {
  for (const platform of Object.keys(enums.notificationPlatforms)) {
    if (user.value[`${platform.toLowerCase()}_notifications`] === true) {
      platforms.value.push(platform);
    }
  }
}

function submit(): void {
  if (valid.value) {
    api
      .update({
        first_name: user.value.first_name,
        last_name: user.value.last_name,
        notification_scope: user.value.notification_scope,
        email_notifications: platforms.value.includes("Email"),
        telegram_notifications: platforms.value.includes("Telegram"),
      })
      .then((response) => {
        user.value = response;
        getPlatforms();
      });
  }
}
</script>
