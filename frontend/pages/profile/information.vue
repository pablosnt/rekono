<template>
  <MenuProfile>
    <v-container fluid>
      <v-row justify="center">
        <v-col cols="8">
          <BaseSection
            v-if="user"
            :title="`@${user.username}`"
            :subtitle="user.email"
            :icon="enums.roles[user.role].icon"
            :color="enums.roles[user.role].color"
          >
            <template #append>
              <p class="text-medium-emphasis">
                Joined on {{ new Date(user.date_joined).toDateString() }}
              </p>
            </template>

            <v-form v-model="valid" @submit.prevent="submit()">
              <v-container fluid>
                <v-row justify="center">
                  <v-col cols="5">
                    <v-text-field
                      v-model="user.first_name"
                      prepend-icon="mdi-card-account-details"
                      label="Name"
                      variant="outlined"
                      :rules="[
                        (n) =>
                          !n || validate.name.test(n.trim()) || 'Invalid name',
                      ]"
                      validate-on="input"
                      clearable
                      @update:model-value="disabled = false"
                    />
                  </v-col>
                  <v-col cols="5">
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
                <v-row justify="center">
                  <v-col cols="10">
                    <BaseSection
                      title="Notifications"
                      title-class="text-subtitle-1"
                      icon="mdi-bell-ring"
                      color="black"
                      variant="outlined"
                    >
                      <v-row justify="space-around">
                        <v-col cols="5">
                          <BaseAutocomplete
                            v-model="user.notification_scope"
                            density="comfortable"
                            variant="outlined"
                            label="Scope"
                            :definition="enums.notificationScopes"
                            :rules="[(s) => !!s || 'Scope is required']"
                            validate-on="input"
                            hide-details
                            @update:model-value="disabled = false"
                          />
                        </v-col>
                        <v-col cols="5">
                          <BaseAutocomplete
                            v-model="platforms"
                            multiple
                            density="comfortable"
                            variant="outlined"
                            label="Platforms"
                            :definition="enums.notificationPlatforms"
                            :disabled="user.notification_scope === 'Disabled'"
                            hide-details
                            clearable
                            chips
                            @update:model-value="disabled = false"
                          />
                        </v-col>
                      </v-row>
                    </BaseSection>
                  </v-col>
                </v-row>

                <v-row class="mt-10" justify="center">
                  <v-col cols="10">
                    <UtilsSubmit text="Save" :disabled="disabled" />
                  </v-col>
                </v-row>
              </v-container>
            </v-form>
          </BaseSection>
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
  platforms.value = [];
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
