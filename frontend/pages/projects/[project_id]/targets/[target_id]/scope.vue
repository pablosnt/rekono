<template>
  <MenuProject>
    <TargetTabs>
      <Dataset
        ref="dataset"
        :api="api"
        :default-parameters="{ ordering: 'port' }"
        :add="TargetPortDialog"
        icon="mdi-antenna"
        empty-head="No Scope Defined"
        empty-text="Define the ports and paths to be scanned and how to authenticate. Otherwise, the whole target address will be scanned"
        auditor
        @load-data="(data) => (ports = data)"
      >
        <template #data>
          <v-table>
            <thead>
              <tr>
                <th class="text-center font-weight-bold">Port</th>
                <th class="text-center font-weight-bold">Path</th>
                <th class="text-center font-weight-bold">Authentication</th>
                <th class="text-center font-weight-bold">Auth Name</th>
                <th class="text-center font-weight-bold">Auth Secret</th>
                <th v-if="autz.isAuditor()" />
              </tr>
            </thead>
            <tbody>
              <tr v-for="port in ports" :key="port.id">
                <td class="text-center">
                  <v-icon class="mr-3" :icon="portUtils.getIcon(port.port)" />{{
                    port.port
                  }}
                </td>
                <td class="text-center">{{ port.path }}</td>
                <td class="text-center">
                  {{ port.authentication ? port.authentication.type : "None" }}
                </td>
                <td class="text-center">
                  {{ port.authentication ? port.authentication.name : "" }}
                </td>
                <td class="text-center">
                  {{ port.authentication ? port.authentication.secret : "" }}
                </td>
                <td v-if="autz.isAuditor()">
                  <v-dialog v-if="!port.authentication" width="auto">
                    <template #activator="{ props: activatorProps }">
                      <BaseButton
                        icon="mdi-key-plus"
                        size="large"
                        color="green"
                        v-bind="activatorProps"
                        tooltip="Add Authentication"
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
                  <UtilsDeleteButton
                    v-if="port.authentication"
                    :id="port.authentication.id"
                    :api="authApi"
                    :text="`Authentication '${port.authentication.name ? port.authentication.name : port.authentication.type}' will be removed`"
                    icon="mdi-key-remove"
                    action="Delete Authentication"
                    @completed="dataset.loadData(false)"
                  />
                  <UtilsDeleteButton
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
        </template>
      </Dataset>
    </TargetTabs>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const TargetPortDialog = resolveComponent("TargetPortDialog");
const portUtils = usePorts();
const autz = useAutz();
const dataset = ref(null);
const ports = ref([]);
const api = useApi("/api/target-ports/", true, "Target port");
const authApi = useApi("/api/authentications/", true, "Authentication");
</script>
