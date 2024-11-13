<template>
  <MenuToolkit>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :add="WordlistDialog"
      icon="mdi-file-word-box"
      empty-head="No Wordlists"
      empty-text="There are no wordlists. Create your first one"
    >
      <template #item="{ item }">
        <v-card
          :title="item.name"
          elevation="2"
          class="mx-auto"
          density="compact"
        >
          <template #append>
            <span class="me-3" />
            <UtilsCounterChip
              :number="item.size"
              entity="Words"
              icon="mdi-counter"
            />
            <span class="me-3" />
            <v-chip>
              <v-icon
                v-if="item.type === 'Subdomain'"
                icon="mdi-routes"
                start
              />
              <p v-if="item.type === 'Endpoint'">
                <strong>/</strong><span class="me-1" />
              </p>
              {{ item.type }}
            </v-chip>
            <span class="me-3" />
            <UtilsOwner :entity="item" />
          </template>

          <v-card-actions>
            <v-spacer />
            <UtilsLike
              :api="api"
              :item="item"
              @reload="(value) => dataset.loadData(value)"
            />
            <span class="me-3" />
            <UtilsDeleteButtonEdit
              v-if="
                (item.owner !== null && item.owner.id === user.user) ||
                user.role === 'Admin'
              "
            >
              <template #edit-dialog="{ isActive }">
                <WordlistDialog
                  :api="api"
                  :edit="item"
                  @completed="dataset.loadData(false)"
                  @close-dialog="isActive.value = false"
                />
              </template>
              <template #delete-dialog="{ isActive }">
                <UtilsDeleteDialog
                  :id="item.id"
                  :api="api"
                  :text="`Wordlist '${item.name}' will be removed`"
                  @completed="dataset.loadData(false)"
                  @close-dialog="isActive.value = false"
                />
              </template>
            </UtilsDeleteButtonEdit>
          </v-card-actions>
        </v-card>
      </template>
    </Dataset>
  </MenuToolkit>
</template>

<script setup lang="ts">
const WordlistDialog = resolveComponent("WordlistDialog");
definePageMeta({ layout: false });
const user = userStore();
const enums = useEnums();
const filters = useFilters();
const dataset = ref(null);
const api = ref(useApi("/api/wordlists/", true, "Wordlist"));
const filtering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      label: "Type",
      icon: "mdi-routes",
      collection: enums.wordlists,
      key: "type",
    },
    {
      type: "switch",
      label: "Mine",
      color: "blue",
      cols: 1,
      key: "owner",
      trueValue: user.user,
      falseValue: null,
    },
    {
      type: "switch",
      label: "Likes",
      color: "red",
      cols: 1,
      key: "like",
      trueValue: true,
      falseValue: null,
    },
    {
      type: "autocomplete",
      label: "Sort",
      icon: "mdi-sort",
      collection: ["id", "name", "type", "size", "likes_count"],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "id",
    },
  ])
  .then((results) => (filtering.value = results));
</script>
