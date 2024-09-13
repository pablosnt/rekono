<template>
  <MenuProject>
    <TabTarget>
      <v-container fluid>
        <v-row justify="center" dense>
          <v-col cols="10">
            <Dataset
              ref="dataset"
              :api="api"
              ordering="port"
              :add="TargetPortDialog"
              icon="mdi-antenna"
              empty-head="No Scopes"
              empty-text="Define the set of ports and paths in the target scope and how to perform the authentication"
              @load-data="(data) => (ports = data)"
            >
              <!-- todo: Review empty-text and use them to provide help about the entities that the user can create -->
              <template #data>
                <v-row justify="center" dense>
                  <v-col cols="10">
                    <v-table density="compact">
                      <thead>
                        <tr>
                          <th class="text-center font-weight-bold">Port</th>
                          <th class="text-center font-weight-bold">Path</th>
                          <th class="text-center font-weight-bold">
                            Authentication
                          </th>
                          <th class="text-center font-weight-bold">
                            Auth Name
                          </th>
                          <th class="text-center font-weight-bold">
                            Auth Secret
                          </th>
                          <th />
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="port in ports" :key="port.id">
                          <td class="text-center">
                            <v-icon
                              class="mr-3"
                              :icon="utils.getIconByPort(port.port)"
                            />{{ port.port }}
                          </td>
                          <td class="text-center">{{ port.path }}</td>
                          <td class="text-center">
                            {{
                              port.authentication
                                ? port.authentication.type
                                : "None"
                            }}
                          </td>
                          <td class="text-center">
                            {{
                              port.authentication
                                ? port.authentication.name
                                : ""
                            }}
                          </td>
                          <td class="text-center">
                            {{
                              port.authentication
                                ? port.authentication.secret
                                : ""
                            }}
                          </td>
                          <td>
                            <!-- mdi-key-plus -->
                            <v-dialog v-if="!port.authentication" width="auto">
                              <template #activator="{ props: activatorProps }">
                                <v-btn
                                  icon="mdi-key-plus"
                                  variant="text"
                                  size="large"
                                  color="green"
                                  v-bind="activatorProps"
                                />
                              </template>
                              <template #default="{ isActive }">
                                <TargetPortAuthenticationDialog
                                  :api="authApi"
                                  :target-port="port.id"
                                  @close-dialog="isActive.value = false"
                                  @completed="
                                    isActive.value = false;
                                    dataset.loadData(false);
                                  "
                                />
                              </template>
                            </v-dialog>
                            <UtilsButtonDelete
                              v-if="port.authentication"
                              :id="port.authentication.id"
                              :api="authApi"
                              :text="`Authentication '${port.authentication.name ? port.authentication.name : port.authentication.type}' will be removed`"
                              icon="mdi-key-remove"
                              action="Delete Authentication"
                              @completed="dataset.loadData(false)"
                            />
                            <UtilsButtonDelete
                              :id="port.id"
                              :api="api"
                              :text="`Target port '${port.port}' will be removed`"
                              :variant="undefined"
                              icon="mdi-minus-network"
                              action="Delete Port"
                              @completed="dataset.loadData(false)"
                            />
                          </td>
                        </tr>
                      </tbody>
                    </v-table>
                  </v-col>
                </v-row>
              </template>
            </Dataset>
          </v-col>
        </v-row>
      </v-container>
    </TabTarget>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const TargetPortDialog = resolveComponent("TargetPortDialog");
const utils = useUtils();
const dataset = ref(null);
const ports = ref([]);
const api = useApi("/api/target-ports/", true, "Target port");
const authApi = useApi("/api/authentications/", true, "Authentication");
</script>
