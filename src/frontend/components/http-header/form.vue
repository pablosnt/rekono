<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-container fluid>
      <v-row justify="center" dense>
        <v-col cols="4">
          <v-text-field
            v-model="key"
            class="text-medium-emphasis"
            variant="outlined"
            label="Header"
            clearable
            validate-on="input"
            :rules="[
              (k) => !!k || 'Header key is required',
              (k) => validate.name.test(k.trim()) || 'Header key is invalid',
            ]"
            :readonly="autz.isAuditor()"
            @update:model-value="disabled = false"
          />
        </v-col>
        <v-col cols="8">
          <v-text-field
            v-model="value"
            variant="outlined"
            label="Value"
            clearable
            validate-on="input"
            :rules="[
              (v) => !!v || 'Header value is required',
              (v) => validate.text.test(v.trim()) || 'Header value is invalid',
            ]"
            :readonly="autz.isAuditor()"
            @update:model-value="disabled = false"
          >
            <template #prepend>:</template>
            <template v-if="header !== null" #append>
              <BaseButton
                v-if="autz.isAuditor()"
                :disabled="disabled"
                icon="mdi-tray-arrow-down"
                icon-color="green"
                tooltip="Save"
                hover
                @click="submit"
              />
              <UtilsDeleteButton
                v-if="autz.isAuditor() && header !== null"
                :id="header.id"
                :api="api"
                :text="`HTTP header '${header.key}' will be removed`"
                @completed="$emit('completed')"
              />
            </template>
          </v-text-field>
        </v-col>
      </v-row>
      <UtilsSubmit
        v-if="!header"
        text="Create"
        class="mt-5"
        :disabled="disabled"
      />
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  header: { type: Object, required: false, default: null },
  parameters: { type: Object, required: false, default: null },
});
const emit = defineEmits(["completed", "loading"]);
const validate = useValidation();
const autz = useAutz();
const valid = ref(true);
const disabled = ref(props.header !== null);
const key = ref(props.header ? props.header.key : null);
const value = ref(props.header ? props.header.value : null);

function submit(): void {
  if (valid.value) {
    let request = null;
    let body = { key: key.value.trim(), value: value.value.trim() };
    if (props.parameters) {
      body = Object.assign(
        {},
        Object.keys(props.parameters)
          .filter((key) => !key.includes("__"))
          .reduce((res, key) => ((res[key] = props.parameters[key]), res), {}),
        body,
      );
    }
    if (props.header) {
      request = props.api.update(body, props.header.id);
    } else {
      request = props.api.create(body);
    }
    emit("loading", true);
    request
      .then((response) => {
        disabled.value = true;
        emit("loading", false);
        emit("completed", response);
      })
      .catch(() => emit("loading", false));
  }
}
</script>
