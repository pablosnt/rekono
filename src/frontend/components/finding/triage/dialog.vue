<template>
  <BaseDialog
    title="Triage"
    :subtitle="
      finding.triage_date
        ? `Last triage on ${new Date(finding.triage_date).toDateString()}`
        : undefined
    "
    :loading="loading"
    width="700"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <template #append>
      <UtilsOwner :entity="finding" field="triage_by" />
    </template>
    <v-form v-model="valid" class="mt-3" @submit.prevent="submit()">
      <v-container fluid>
        <v-row justify="center" dense>
          <v-col cols="11">
            <v-autocomplete
              v-model="status"
              auto-select-first
              density="comfortable"
              variant="outlined"
              label="Mode"
              :items="Object.keys(enums.triage)"
              validate-on="input"
              :rules="[(s) => !!s || 'Status is required']"
              :prepend-inner-icon="
                status ? enums.triage[status].icon : undefined
              "
              :color="status ? enums.triage[status].color : undefined"
              @update:model-value="disabled = false"
            >
              <template #item="{ props: formatProps, item }">
                <v-list-item
                  v-bind="formatProps"
                  :title="item.raw"
                  :prepend-icon="enums.triage[item.raw].icon"
                  :color="enums.triage[item.raw].color"
                />
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
        <v-row justify="center" dense>
          <v-col cols="11">
            <v-textarea
              v-model="comment"
              label="Comment"
              variant="outlined"
              :rules="[
                (c) => !c || validate.text.test(c) || 'Invalid comment value',
                (c) =>
                  !c ||
                  c.length <= 300 ||
                  'Comment must be 300 characters or less',
              ]"
              validate-on="input"
              auto-grow
              max-rows="6"
              rows="3"
              @update:model-value="disabled = false"
            />
          </v-col>
        </v-row>
        <v-row>
          <UtilsSubmit :disabled="disabled" text="Triage" />
        </v-row>
      </v-container>
    </v-form>
  </BaseDialog>
</template>

<script setup lang="ts">
const props = defineProps({ api: Object, finding: Object });
const emit = defineEmits(["closeDialog", "completed"]);
const enums = ref(useEnums());
const validate = useValidation();
const loading = ref(false);
const valid = ref(true);
const disabled = ref(true);
const status = ref(props.finding.triage_status);
const comment = ref(props.finding.triage_comment);

function submit(): void {
  if (valid.value) {
    loading.value = true;
    props.api
      .update(
        { triage_status: status.value, triage_comment: comment.value },
        props.finding.id,
      )
      .then((response) => {
        loading.value = false;
        emit("completed", response);
      })
      .catch(() => (loading.value = false));
  }
}
</script>
