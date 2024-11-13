<template>
  <BaseDialog title="New Project Member" :loading="loading">
    <v-container>
      <v-form v-model="valid" @submit.prevent="submit()">
        <v-autocomplete
          v-model="newMembers"
          clearable
          chips
          auto-select-first
          density="comfortable"
          variant="outlined"
          label="Users"
          :items="users"
          item-title="email"
          item-value="id"
          multiple
          :rules="[(m) => m.length > 0 || 'Member is required']"
          validate-on="input" />
        <BaseButtonSubmit
          text="Add"
          class="mt-5"
          :disabled="newMembers.length === 0"
      /></v-form>
      <UtilsPercentage
        v-if="loading"
        :total="newMembers.length"
        :progress="progress"
      />
    </v-container>
  </BaseDialog>
</template>

<script setup lang="ts">
const props = defineProps({ api: Object, parameters: Object });
const emit = defineEmits(["completed"]);
const alert = useAlert();
const users = ref([]);
const newMembers = ref([]);
const loading = ref(false);
const progress = ref(0);
const valid = ref(true);
const addApi = useApi(`/api/projects/${props.parameters.project}/members/`);

props.api
  .list({ is_active: true, no_project: props.parameters.project }, true)
  .then((response) => (users.value = response.items));

function submit(): void {
  loading.value = true;
  let errors = 0;
  for (const newMember of newMembers.value) {
    addApi
      .create({ user: newMember })
      .then(() => {
        progress.value++;
        if (errors + progress.value === newMembers.value.length) {
          loading.value = false;
          if (errors > 0) {
            alert("Some users couldn't be added to the project", "warning");
          }
          emit("completed");
        }
      })
      .catch(() => {
        errors++;
        if (errors + progress.value === newMembers.value.length) {
          loading.value = false;
          if (progress.value > 0) {
            alert("Some users couldn't be added to the project", "warning");
            emit("completed");
          } else {
            alert("Users couldn't be added to the project", "error");
          }
        }
      });
  }
}
</script>
