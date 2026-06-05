<template>
  <div class="space-y-4 mx-auto mt-3">
    <UFormField
      v-if="supportedWordlist"
      :required="requiredWordlist"
      label="Wordlists"
      name="wordlists"
    >
      <USelectMenu
        :model-value="wordlists"
        multiple
        class="w-full"
        icon="i-mdi-file-word"
        placeholder="Select the wordlists to use"
        :items="wordlistOptions"
        value-key="id"
        label-key="name"
        description-key="type"
        :filter-fields="['name', 'type']"
        size="xl"
        @update:model-value="
          (value) => {
            wordlists = value;
            $emit('update-wordlists', wordlists);
          }
        "
      >
        <template #trailing>
          <UIcon
            v-if="wordlists.length === 0"
            class="group-data-[state=open]:rotate-180 transition-transform duration-200"
            name="i-lucide-chevron-down"
          />
          <UButton
            v-else
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            size="sm"
            aria-label="Clear wordlists"
            @click="wordlists = []"
          />
        </template>
      </USelectMenu>
    </UFormField>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  api: typeof useApi;
  supportedWordlist: boolean;
  requiredWordlist: boolean;
}>();
defineEmits<{
  "update-wordlists": [newWordlists: Array<number>];
}>();

const wordlists = ref([]);
const wordlistOptions = ref([]);

function loadWordlists() {
  props.api.list("wordlists/", {}, true).then((response) => {
    wordlistOptions.value = response.items;
  });
}

watch(
  () => props.supportedWordlist,
  () =>
    props.supportedWordlist && wordlistOptions.value.length === 0
      ? loadWordlists()
      : null,
);
</script>
