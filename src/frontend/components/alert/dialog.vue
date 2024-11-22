<template>
  <BaseDialog
    title="Create Report"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <v-form v-model="valid" class="mt-3" @submit.prevent="submit()">
      <v-container fluid>
        <v-row v-if="edit === null" justify="space-around" dense>
          <v-col cols="4">
            <v-autocomplete
              v-model="mode"
              auto-select-first
              density="comfortable"
              variant="outlined"
              label="Mode"
              :items="Object.keys(enums.alertModes)"
              clearable
              validate-on="input"
              :rules="[(m) => !!m || 'Mode is required']"
              :prepend-inner-icon="
                mode ? enums.alertModes[mode].icon : undefined
              "
            />
          </v-col>
          <v-col>
            <!-- TODO: Review validation in all forms -->
            <v-autocomplete
              v-model="item"
              auto-select-first
              density="comfortable"
              variant="outlined"
              label="Item"
              :items="
                mode !== null
                  ? Object.keys(enums.alertItems).filter((item) => {
                      return (
                        mode === 'New' ||
                        enums.alertItems[item][mode.toLowerCase()] !== null
                      );
                    })
                  : []
              "
              :disabled="!mode"
              clearable
              validate-on="input"
              :rules="[(i) => !!i || 'Item is required']"
              :prepend-inner-icon="
                item ? enums.alertItems[item].icon : undefined
              "
            />
          </v-col>
          <v-col cols="3">
            <v-switch
              v-model="subscribe"
              color="red"
              label="Subscribe members"
            />
          </v-col>
        </v-row>
        <v-row justify="space-around" dense>
          <v-col>
            <v-text-field
              v-model="value"
              type="text"
              :disabled="mode !== 'Filter'"
              :label="
                mode === 'Filter' && item
                  ? `Filter by '${item === 'CVE' ? item : enums.alertItems[item].filter}'`
                  : 'Filter value'
              "
              :prepend-inner-icon="enums.alertModes.Filter.icon"
              variant="outlined"
              :rules="[
                (v) => mode !== 'Filter' || !!v || 'Value is required',
                (v) => !v || validate.name.test(v.trim()) || 'Invalid value',
              ]"
              validate-on="input"
              clearable
            />
          </v-col>
        </v-row>
        <v-row>
          <UtilsSubmit :text="!edit ? 'Create' : 'Update'" />
        </v-row>
      </v-container>
    </v-form>
  </BaseDialog>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  parameters: { type: Object, required: false, default: null },
  edit: { type: Object, required: false, default: null },
});
const emit = defineEmits(["closeDialog", "completed"]);
const validate = useValidation();
const enums = ref(useEnums());
const valid = ref(true);
const loading = ref(false);
const mode = ref(null);
const item = ref(null);
const value = ref(null);
if (props.edit) {
  mode.value = props.edit.mode;
  item.value = props.edit.item;
  value.value = props.edit.value;
}
const subscribe = ref(false);

function submit(): void {
  if (valid.value) {
    loading.value = true;
    let request = null;
    if (props.edit === null) {
      request = props.api.create({
        project: props.parameters.project,
        item: item.value,
        mode: mode.value,
        value: value.value,
        subscribe_all_members: subscribe.value,
      });
    } else {
      request = props.api.update({ value: value.value }, props.edit.id);
    }
    request
      .then((response) => {
        loading.value = false;
        emit("completed", response);
      })
      .catch(() => {
        loading.value = false;
      });
  }
}
</script>
