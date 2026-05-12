<template>
  <div class="space-y-4 mx-auto mt-3">
    <UFormField :required="required" label="Technologies" name="technologies">
      <USelectMenu
        :model-value="technologies"
        create-item="always"
        multiple
        class="w-full"
        icon="i-lucide-code"
        placeholder="Select the technologies to use"
        :items="technologyOptions"
        value-key="id"
        label-key="name"
        description-key="version"
        :filter-fields="['name', 'version']"
        size="xl"
        @update:model-value="
          (value) => {
            technologies = value;
            $emit('update-technologies', technologies);
          }
        "
        @create="createTechnology"
      >
        <template #create-item-label="{ item }">
          Create "{{ item }}"{{
            item.includes(" - ") ? "" : " (format {technology} - {version})"
          }}
        </template>
        <template #trailing>
          <UIcon
            v-if="technologies.length === 0"
            class="group-data-[state=open]:rotate-180 transition-transform duration-200"
            name="i-lucide-chevron-down"
          />
          <UButton
            v-else
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            size="sm"
            aria-label="Clear technologies"
            @click="technologies = []"
          />
        </template>
      </USelectMenu>
    </UFormField>
  </div>
</template>

<script setup lang="ts">
import * as z from "zod";

const props = defineProps<{
  api: typeof useApi;
  required: boolean;
}>();
const emit = defineEmits<{
  "update-technologies": [newTechnologies: Array<number>];
}>();

const validation = useValidation();
const toast = useToast();
const technologies = ref([]);
const technologyOptions = ref([]);
const schema = z.object({
  name: validation.name(),
  version: validation.name("version", false),
});

function loadTechnologies() {
  props.api.list("parameters/technologies/", {}, true).then((response) => {
    technologyOptions.value = response.items;
  });
}

function createTechnology(value: string) {
  let name = value;
  let version = null;
  let split = null;
  if (value.includes(" - ")) {
    split = " - ";
  } else if (value.includes("-")) {
    split = "-";
  }
  if (split) {
    const aux = value.split(split, 2);
    name = aux[0];
    version = aux[1];
  }
  try {
    schema.parse({ name: name, version: version });
  } catch {
    toast.add({
      title: "Error",
      description: "Invalid new technology value",
      color: "error",
    });
    return;
  }
  props.api
    .create(
      "parameters/technologies/",
      { name: name, version: version },
      {},
      "Technology",
    )
    .then((response) => {
      technologyOptions.value.push(response);
      technologies.value.push(response.id);
      emit("update-technologies", technologies.value);
    });
}

watch(
  () => props.required,
  () =>
    props.required && technologyOptions.value.length === 0
      ? loadTechnologies()
      : null,
);
</script>
