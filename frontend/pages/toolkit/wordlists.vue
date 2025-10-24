<template>
  <MenuToolkit>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :add="WordlistDialog"
      icon="mdi-file-word-box"
      empty-head="No Wordlists"
      empty-text="Create one to use it as dictionary for enumeration scans"
      cols="5"
    >
      <template #item="{ item }">
        <v-card
          :title="item.name"
          :subtitle="`${utils.displayNumber(item.size)} words`"
          elevation="2"
          class="ma-3"
          density="comfortable"
        >
          <template #prepend>
            <BaseButton
              :icon="enums.wordlists[item.type].icon"
              :tooltip="item.type"
              @click.prevent.stop
            />
          </template>
          <template #append>
            <UtilsLike
              class="mr-4"
              :api="api"
              :item="item"
              @reload="(value) => dataset.loadData(value)"
            />
            <UtilsOwner :entity="item" />
            <UtilsDeleteButtonEdit v-if="autz.isAdmin() || autz.isOwner(item)">
              <template #edit-dialog="{ isActive }">
                <WordlistDialog
                  :api="api"
                  :edit="item"
                  @completed="
                    dataset.loadData(false);
                    isActive.value = false;
                  "
                  @close-dialog="isActive.value = false"
                />
              </template>
              <template #delete-dialog="{ isActive }">
                <UtilsDeleteDialog
                  :id="item.id"
                  :api="api"
                  :text="`Wordlist '${item.name}' will be removed`"
                  @completed="
                    dataset.loadData(false);
                    isActive.value = false;
                  "
                  @close-dialog="isActive.value = false"
                />
              </template>
            </UtilsDeleteButtonEdit>
          </template>
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
const utils = useUtils();
const autz = useAutz();
const dataset = ref(null);
const api = ref(useApi("/api/wordlists/", true, "Wordlist"));
const filtering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      label: "Type",
      icon: "mdi-tag",
      collection: filters.collectionFromEnum(enums.wordlists),
      fieldValue: "name",
      fieldTitle: "name",
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
