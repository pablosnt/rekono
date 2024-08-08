<template>
  <Dataset
    ref="dataset"
    :api="api"
    :filtering="filtering"
    :add="handleMember ? DialogAddMember : DialogInviteUser"
    :default-parameters="project ? { project: project } : null"
    ordering="id"
    @load-data="(data) => (users = data)"
  >
    <template #data>
      <v-row dense>
        <v-col v-for="user in users" :key="user.id" cols="4">
          <v-card
            elevation="3"
            class="mx-auto"
            density="compact"
            :title="
              user.first_name && user.last_name
                ? `${user.first_name} ${user.last_name}`
                : user.email
            "
            :subtitle="user.username ? `@${user.username}` : undefined"
          >
            <template #prepend>
              <v-menu min-width="200px" rounded>
                <template #activator="{ props }">
                  <v-btn icon v-bind="props">
                    <v-avatar variant="outlined">
                      <v-icon
                        :icon="
                          user.is_active
                            ? enums.roles[user.role].icon
                            : 'mdi-cancel'
                        "
                        :color="
                          user.is_active ? enums.roles[user.role].color : 'grey'
                        "
                        size="x-large"
                      />
                    </v-avatar>
                  </v-btn>
                </template>
                <v-card>
                  <template #text>
                    <v-card-text>
                      <div class="mx-auto text-center">
                        <v-avatar variant="outlined">
                          <v-icon
                            :icon="enums.roles[user.role].icon"
                            :color="enums.roles[user.role].color"
                            size="x-large"
                          />
                        </v-avatar>
                        <h3 class="mt-2">
                          {{
                            user.first_name
                              ? `${user.first_name} ${user.last_name}`
                              : user.email
                          }}
                        </h3>
                        <p v-if="user.username" class="text-primary mt-2">
                          {{ `@${user.username}` }}
                        </p>
                        <v-btn
                          v-if="user.first_name"
                          class="pa-0 text-none"
                          color="primary"
                          variant="text"
                          :text="user.email"
                          :href="`mailto:${user.email}`"
                        />
                        <p
                          v-if="user.username"
                          class="text-medium-emphasis mt-2"
                        >
                          Joined on
                          {{ new Date(user.date_joined).toDateString() }}
                        </p>
                        <div v-if="user.id !== current.user">
                          <v-divider class="my-3" />
                          <div v-if="changeRole">
                            <v-autocomplete
                              v-model="user.role"
                              auto-select-first
                              density="comfortable"
                              variant="underlined"
                              :prepend-inner-icon="enums.roles[user.role].icon"
                              :color="enums.roles[user.role].color"
                              label="Role"
                              :items="roles"
                              :rules="[(r) => !!r || 'Role is required']"
                              validate-on="input"
                              hide-details
                              @update:model-value="
                                api
                                  .update({ role: user.role }, user.id)
                                  .then((response) => {
                                    user = response;
                                    dataset.loadData(false);
                                  })
                              "
                              @click.stop
                            />
                            <v-divider class="my-3" />
                          </div>
                          <v-btn
                            v-if="enableDisable && user.username"
                            :color="user.is_active ? 'red' : 'green'"
                            :text="user.is_active ? 'Disable' : 'Enable'"
                            variant="tonal"
                            block
                            @click.stop="enableOrDisable(user)"
                          />
                          <v-dialog
                            v-if="handleMember"
                            width="500"
                            class="overflow-auto"
                          >
                            <template #activator="{ props: activatorProps }">
                              <v-btn
                                v-bind="activatorProps"
                                color="red"
                                text="Remove Member"
                                variant="tonal"
                                block
                              />
                            </template>
                            <template #default="{ isActive }">
                              <DialogDelete
                                :id="user.id"
                                :api="removeMemberApi"
                                :text="`Project member '${user.email}' will be removed`"
                                @completed="
                                  dataset.loadData(false);
                                  isActive.value = false;
                                "
                                @close-dialog="isActive.value = false"
                              />
                            </template>
                          </v-dialog>
                        </div>
                      </div>
                    </v-card-text>
                  </template>
                </v-card>
              </v-menu>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </Dataset>
</template>

<script setup lang="ts">
const props = defineProps({
  project: {
    type: Number,
    required: false,
    default: null,
  },
  changeRole: {
    type: Boolean,
    required: false,
    default: false,
  },
  enableDisable: {
    type: Boolean,
    required: false,
    default: false,
  },
  handleMember: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const current = userStore();
const enums = ref(useEnums());
const roles = ref(Object.keys(enums.value.roles));
const api = useApi("/api/users/", true);
const removeMemberApi = props.project
  ? useApi(`/api/projects/${props.project}/members/`, true, "Project member")
  : null;
const users = ref([]);
const filtering = ref([
  {
    type: "autocomplete",
    label: "Role",
    icon: "mdi-diamond",
    collection: roles.value,
    key: "role",
    value: null,
  },
  {
    type: "switch",
    label: "Active",
    color: "green",
    cols: 2,
    key: "is_active",
    trueValue: true,
    falseValue: null,
    value: null,
  },
  {
    type: "autocomplete",
    label: "Sort",
    icon: "mdi-sort",
    collection: ["id", "username", "email", "name", "date_joined"],
    fieldValue: "id",
    fieldTitle: "name",
    key: "ordering",
    value: "id",
  },
]);
const dataset = ref(null);
const alert = useAlert();

const DialogInviteUser = resolveComponent("DialogInviteUser");
const DialogAddMember = resolveComponent("DialogAddMember");

function enableOrDisable(user) {
  let request = null;
  let message = user.username ? user.username : user.email;
  if (user.is_active) {
    request = api.remove(user.id);
    message = `User ${message} has been disabled`;
  } else {
    request = api.create({}, user.id, "enable/");
    message = `User ${message} has been enabled`;
  }
  request.then(() => {
    dataset.value.loadData(false);
    alert(message, message.includes("disabled") ? "warning" : "success");
  });
}
</script>
