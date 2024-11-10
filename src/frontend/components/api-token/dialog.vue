<template>
  <Dialog
    title="New API Token"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <v-form v-model="valid" @submit.prevent="submit()">
      <v-conatiner v-if="!key" fluid>
        <v-text-field
          v-model="name"
          class="mt-2"
          label="Name"
          variant="outlined"
          :rules="[
            (n) => !!n || 'Name is required',
            (n) => validate.name.test(n) || 'Invalid name value',
          ]"
          validate-on="input"
        />

        <v-text-field
          v-model="expiration"
          :model-value="expiration.toDateString()"
          :active="dateMenu"
          label="Date"
          prepend-inner-icon="mdi-calendar"
          variant="underlined"
          readonly
          :rules="[(e) => !!e || 'Expiration is required']"
          validate-on="input"
        >
          <v-menu
            v-model="dateMenu"
            :close-on-content-click="false"
            activator="parent"
            transition="scale-transition"
          >
            <v-date-picker
              v-if="dateMenu"
              v-model="expiration"
              show-adjacent-months
              :min="minExpiration.toISOString().split('T')[0]"
            >
              <template #actions>
                <v-btn
                  text="Clear"
                  @click="expiration = getDefaultExpiration()"
                />
              </template>
            </v-date-picker>
          </v-menu>
        </v-text-field>
        <UtilsButtonSubmit text="Create" />
      </v-conatiner>
      <v-container v-if="key" fluid>
        <v-row justify="center" dense>
          <v-col cols="10">
            <v-alert
              class="text-center"
              color="info"
              icon="$info"
              variant="tonal"
              text="This is the last time you can see your API key's value. Save it safely"
            />
          </v-col>
        </v-row>
        <v-row justify="center" dense>
          <v-col cols="8">
            <v-text-field
              v-model="key"
              bg-color="green"
              variant="outline"
              readonly
              prepend-inner-icon="mdi-api"
              append-inner-icon="mdi-bookmark-multiple-outline"
              @click:append-inner="copyKey()"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-form>
  </Dialog>
</template>

<script setup lang="ts">
const props = defineProps({ api: Object });
const emit = defineEmits(["closeDialog", "completed"]);
const validate = useValidation();
const alert = useAlert();
const name = ref(null);
const expiration = ref(getDefaultExpiration());
const minExpiration = ref(new Date());
minExpiration.value.setDate(minExpiration.value.getDate() + 1);
const key = ref(null);
const valid = ref(true);
const loading = ref(false);
const dateMenu = ref(false);

function getDefaultExpiration(): Date {
  const date = new Date();
  date.setFullYear(date.getFullYear() + 1);
  return date;
}

function submit(): void {
  if (valid.value) {
    loading.value = true;
    expiration.value.setUTCHours(23);
    expiration.value.setUTCMinutes(0);
    expiration.value.setUTCMilliseconds(0);
    expiration.value.setUTCSeconds(0);
    props.api
      .create({
        name: name.value.trim(),
        expiration: expiration.value.toISOString(),
      })
      .then((response) => {
        key.value = response.key;
        loading.value = false;
        emit("completed", response);
      })
      .catch(() => (loading.value = false));
  }
}

function copyKey(): void {
  navigator.clipboard.writeText(key.value);
  alert("API token copied to the clipboard", "success");
}
</script>
