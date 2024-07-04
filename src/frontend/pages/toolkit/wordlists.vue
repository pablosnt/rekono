<template>
  <MenuToolkit>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :add="DialogWordlist"
      icon="mdi-file-word-box"
      empty="There are no wordlists"
      @load-data="(data) => (wordlists = data)"
    >
      <template #data>
        <v-row dense>
          <v-col v-for="wordlist in wordlists" :key="wordlist.id" cols="6">
            <v-card
              :title="wordlist.name"
              elevation="4"
              class="mx-auto"
              density="compact"
            >
              <template #append>
                <span class="me-3" />
                <v-chip v-if="wordlist.size" color="red">
                  <v-icon icon="mdi-counter" start />
                  {{
                    wordlist.size < 1000
                      ? wordlist.size
                      : Math.floor(wordlist.size / 1000).toString() + "k"
                  }}
                  Words
                </v-chip>
                <span class="me-3" />
                <v-chip>
                  <v-icon
                    v-if="wordlist.type === 'Subdomain'"
                    icon="mdi-routes"
                    start
                  />
                  <p v-if="wordlist.type === 'Endpoint'">
                    <strong>/</strong><span class="me-1" />
                  </p>
                  {{ wordlist.type }}
                </v-chip>
                <span class="me-3" />
                <v-chip
                  v-if="wordlist.owner"
                  color="primary"
                  :variant="wordlist.owner.id === user.user ? 'flat' : 'tonal'"
                >
                  <v-icon icon="mdi-at" start />
                  {{ wordlist.owner.username }}
                </v-chip>
                <v-chip v-if="!wordlist.owner">Default</v-chip>
                <span class="me-3" />
                <ButtonLike
                  :api="api"
                  :item="wordlist"
                  @reload="(value) => dataset.loadData(value)"
                />
                <span class="me-3" />
                <ButtonEditDelete
                  v-if="
                    (wordlist.owner !== null &&
                      wordlist.owner.id === user.user) ||
                    user.role === 'Admin'
                  "
                >
                  <template #edit-dialog="{ isActive }">
                    <DialogWordlist
                      :api="api"
                      :edit="wordlist"
                      @completed="dataset.loadData(false)"
                      @close-dialog="isActive.value = false"
                    />
                  </template>
                  <template #delete-dialog="{ isActive }">
                    <DialogDelete
                      :id="wordlist.id"
                      :api="api"
                      :text="`Wordlist '${wordlist.name}' will be removed`"
                      @completed="dataset.loadData(false)"
                      @close-dialog="isActive.value = false"
                    />
                  </template>
                </ButtonEditDelete>
              </template>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </Dataset>
  </MenuToolkit>
</template>

<script setup lang="ts">
const DialogWordlist = resolveComponent("DialogWordlist");
definePageMeta({ layout: false });
defineEmits(["loadData"]);
const user = userStore();
const enums = useEnums();
const dataset = ref(null);
const wordlists = ref(null);
const api = ref(useApi("/api/wordlists/", true, "Wordlist"));
const filtering = ref([
  {
    type: "autocomplete",
    label: "Type",
    icon: "mdi-routes",
    collection: enums.wordlists,
    key: "type",
    value: null,
  },
  {
    type: "switch",
    label: "Mine",
    color: "blue",
    cols: 1,
    key: "owner",
    trueValue: user.user,
    falseValue: null,
    value: null,
  },
  {
    type: "switch",
    label: "Likes",
    color: "red",
    cols: 1,
    key: "like",
    trueValue: true,
    falseValue: null,
    value: null,
  },
  {
    type: "autocomplete",
    label: "Sort",
    icon: "mdi-sort",
    collection: ["id", "name", "type", "size", "likes_count"],
    fieldValue: "id",
    fieldTitle: "name",
    key: "ordering",
    value: "id",
  },
]);
</script>
