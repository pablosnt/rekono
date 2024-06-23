<template>
  <NuxtLayout name="header">
    <v-main>
      <Dataset
        ref="dataset"
        :api="api"
        :filtering="filtering"
        icon="mdi-folder-open"
        :empty="
          user.role === 'Admin'
            ? 'Create your first project to start hacking'
            : 'There are no projects yet. Ask your administrator for one'
        "
        @load-data="(data) => (projects = data)"
      >
        <template #data>
          <v-row dense>
            <v-col v-for="project in projects" :key="project.id" cols="4">
              <v-card
                :title="project.name"
                elevation="4"
                class="mx-auto"
                density="compact"
                hover
                :to="`/projects/${project.id}`"
              >
                <template #prepend>
                  <v-avatar color="red-accent-4">
                    <span class="text-h5 text">{{
                      project.name.charAt(0).toUpperCase()
                    }}</span>
                  </v-avatar>
                  <span class="me-2" />
                </template>
                <template #append>
                  <v-chip
                    v-if="project.targets"
                    color="red"
                    :to="`/projects/${project.id}/targets`"
                    @click.stop
                  >
                    <v-icon icon="mdi-target" start />
                    {{ project.targets.length }} Targets
                  </v-chip>
                  <span class="me-3" />
                  <v-chip
                    v-if="project.owner"
                    color="primary"
                    :variant="project.owner.id === user.user ? 'flat' : 'tonal'"
                  >
                    <v-icon icon="mdi-at" start />
                    {{ project.owner.username }}
                  </v-chip>
                </template>
                <template #text>
                  <v-card-text>
                    <p>{{ project.description }}</p>
                    <div v-if="project.tags.length > 0">
                      <v-divider class="mt-3 mb-3" />
                      <v-chip-group selected-class="v-chip">
                        <v-chip
                          v-for="tag in project.tags"
                          :key="tag"
                          size="small"
                        >
                          {{ tag }}
                        </v-chip>
                      </v-chip-group>
                    </div>
                  </v-card-text>

                  <v-card-actions @click.stop>
                    <v-dialog width="auto">
                      <template #activator="{ props: activatorProps }">
                        <v-btn
                          hover
                          icon
                          size="x-large"
                          v-bind="activatorProps"
                          @click.prevent.stop
                        >
                          <v-icon icon="mdi-play-circle" color="green" />
                          <v-tooltip activator="parent" text="Run" />
                        </v-btn>
                      </template>
                      <template #default="{ isActive }">
                        <DialogTask
                          :project="project"
                          @close-dialog="isActive.value = false"
                        />
                      </template>
                    </v-dialog>
                    <v-spacer />
                    <v-btn
                      variant="text"
                      target="_blank"
                      :href="integration.reference"
                      @click.stop
                    >
                      <v-avatar size="small" :image="integration.icon" />
                    </v-btn>
                    <ButtonEditDelete
                      v-if="
                        project.owner.id === user.user || user.role === 'Admin'
                      "
                    >
                      <template #edit-dialog="{ isActive }">
                        <!-- TODO: Dialog to edit project -->
                      </template>
                      <template #delete-dialog="{ isActive }">
                        <DialogDelete
                          :id="project.id"
                          :api="api"
                          :text="`Project '${project.name}' will be removed`"
                          @completed="$emit('reload', false)"
                          @close-dialog="isActive.value = false"
                        />
                      </template>
                    </ButtonEditDelete>
                  </v-card-actions>
                </template>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </Dataset>
    </v-main>
  </NuxtLayout>
</template>

<!-- TODO: Add, defect-dojo sync (create dialog to enable, disable, and click links to the products / engagements) -->

<script setup lang="ts">
const dataset = ref(null);
const projects = ref(null);
const router = useRouter();
const user = userStore();
const api = ref(useApi("/api/projects/", true, "Project"));
const filtering = ref([]);

const integration = ref(null);
const integrationsApi = useApi("/api/integrations/", true);
integrationsApi.get(1).then((response) => (integration.value = response));
</script>
