<template>
  <DialogDefault title="New Project Member" :loading="loading">
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
        <ButtonSubmit
          text="Add"
          class="mt-5"
          :disabled="newMembers.length === 0"
      /></v-form>
      <ShowPercentage
        v-if="loading"
        :total="newMembers.length"
        :progress="progress"
      />
    </v-container>
  </DialogDefault>
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

function submit() {
  loading.value = true;
  let errors = 0;
  for (let i = 0; i < newMembers.value.length; i++) {
    addApi
      .create({ user: newMembers.value[i] })
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
