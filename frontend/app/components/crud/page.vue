<template>
  <!-- TODO: Improve compartimentability of the CrudPage. At the end too many components in the same place, right? -->
  <!-- TODO: Fix typecheck -->
  <div class="flex flex-col h-full w-full">
    <div class="flex-1 overflow-auto">
      <template v-if="config.canRead">
        <div class="container mx-auto max-w-screen-2xl">
          <CrudHeader
            :api="api"
            :open-create-modal="openCreateModal"
            :config="config"
            :state="state"
            :table="tableRef"
            @search="
              (search) => {
                state.searchQuery = search;
                fetchFirstPage();
              }
            "
            @filters="
              (filters) => {
                state.filters = filters;
                fetchFirstPage();
              }
            "
            @ordering="
              (sorting) => {
                state.ordering = sorting;
                fetchFirstPage();
              }
            "
            @create="fetch()"
            @open-create-modal="(open) => (openCreateModal = open)"
          />

          <UEmpty
            v-if="state.items.length === 0 && !state.loading"
            class="mt-10"
            :title="`No ${config.entityNamePlural.toLowerCase()} found`"
            :description="`It looks like you don\'t have access to any ${config.entityName.toLowerCase()} yet. ${config.canCreate ? 'You can create one below.' : 'Please contact your administrator.'}`"
            :icon="config.icon"
            :actions="
              config.canCreate
                ? [
                    {
                      icon: 'i-lucide-plus',
                      label: 'Create new',
                      onClick: () => {
                        openCreateModal = true;
                      },
                    },
                  ]
                : []
            "
            size="xl"
            variant="naked"
          />

          <CrudTable
            v-if="config.tableColumns"
            v-show="state.items.length > 0 || state.loading"
            ref="tableRef"
            :config="config"
            :state="state"
            @edit="
              (item) => {
                selectedItem = item;
                openEditModal = true;
              }
            "
            @delete="
              (item) => {
                selectedItem = item;
                openDeleteModal = true;
              }
            "
          />

          <!-- todo: Cards -->

          <UModal
            v-if="config.canEdit"
            :open="openEditModal"
            :title="`Edit ${config.entityName}`"
            :ui="{ content: 'sm:max-w-3xl sm:max-h-xl', footer: 'justify-end' }"
            @update:open="(open) => (openEditModal = open)"
          >
            <template #body>
              <CrudForm
                ref="editFormRef"
                :api="api"
                :config="config"
                :entity="selectedItem"
                @submit="
                  fetch();
                  openEditModal = false;
                  selectedItem = null;
                "
              />
            </template>
            <template #footer="{ close }">
              <UButton
                label="Cancel"
                color="neutral"
                variant="outline"
                @click="close"
              />
              <UButton
                color="primary"
                label="Save"
                @click="editFormRef.submit()"
              />
            </template>
          </UModal>

          <UModal
            v-if="config.canDelete"
            :open="openDeleteModal"
            :title="`Delete ${config.entityName}`"
            :ui="{ content: 'sm:max-w-3xl sm:max-h-xl', footer: 'justify-end' }"
            :loading="deleteLoading"
            @update:open="(open) => (openDeleteModal = open)"
          >
            <template #body>
              <template v-if="selectedItem">
                <template
                  v-for="(message, index) in config.deleteMessage(selectedItem)"
                  :key="index"
                >
                  <p :class="message.class">
                    {{ message.text }}
                  </p>
                </template>
              </template>
            </template>
            <template #footer="{ close }">
              <UButton
                label="Cancel"
                color="neutral"
                variant="outline"
                @click="close"
              />
              <UButton
                color="primary"
                label="Delete"
                :loading="deleteLoading"
                @click="remove()"
              />
            </template>
          </UModal>

          <div
            v-if="state.total > state.items.length"
            class="grid grid-cols-3 items-center mt-5 px-3"
          >
            <div class="text-sm text-gray-500">
              Showing
              <span class="font-medium">{{
                (state.page - 1) * state.pageSize + 1
              }}</span>
              to
              <span class="font-medium">{{
                Math.min(state.page * state.pageSize, state.total)
              }}</span>
              of
              <span class="font-medium">{{ state.total }}</span>
              results
            </div>
            <div class="flex justify-center">
              <UPagination
                v-model:page="state.page"
                :total="state.total"
                :items-per-page="state.pageSize"
                show-edges
                color="neutral"
                variant="ghost"
                size="lg"
                @update:model-value="fetch()"
              />
            </div>
            <div
              class="flex justify-end items-center gap-2 text-sm text-gray-500"
            >
              <span>Items per page</span>
              <USelect
                v-model="state.pageSize"
                :items="config.pageSizeOptions?.filter((i) => i <= state.total)"
                size="sm"
                @update:model-value="fetch()"
              />
            </div>
          </div>
        </div>
      </template>

      <template v-else>
        <UEmpty
          class="mt-20"
          title="Access Denied"
          description="You do not have the necessary permissions to view this page"
          icon="i-lucide-shield-ban"
          :actions="[
            {
              icon: 'i-lucide-home',
              label: 'Home',
              to: '/',
            },
          ]"
          size="xl"
          variant="naked"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";

const props = defineProps<{ config: CrudConfig<T> }>();
const api = useApi(props.config.endpoint);
const tableRef = ref(null);
const editFormRef = ref(null);
const openCreateModal = ref(false);
const openEditModal = ref(false);
const openDeleteModal = ref(false);
const deleteLoading = ref(false);
const selectedItem = ref(null);

const state = reactive<CrudState<T>>({
  items: [],
  total: 0,
  loading: true,
  page: 1,
  pageSize: props.config.pageSize || 24,
  filters: {},
  ordering: props.config.defaultOrdering,
});

function fetch() {
  state.loading = true;
  let params = state.filters;
  if (props.config.searchable && state.searchQuery) {
    params = { ...params, search: state.searchQuery };
  }
  if (state.ordering) {
    params = { ...params, ordering: state.ordering };
  }
  api
    .list("", params, false, state.page, state.pageSize)
    .then((response) => {
      state.items = response.items;
      state.total = response.total;
    })
    .finally(() => {
      state.loading = false;
    });
}

function remove() {
  deleteLoading.value = true;
  api
    .remove(`${selectedItem.value.id}/`, {}, props.config.entityName)
    .then(() => {
      fetch();
    })
    .finally(() => {
      deleteLoading.value = false;
      openDeleteModal.value = false;
      selectedItem.value = null;
    });
}

function fetchFirstPage() {
  state.page = 1;
  fetch();
}

onMounted(() => {
  if (props.config.canRead) {
    fetch();
  }
});
</script>
