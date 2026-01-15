<template>
  <div class="space-y-4 mx-auto mt-3">
    <UFormField
      :required="required"
      label="Vulnerabilities"
      name="vulnerabilities"
    >
      <USelectMenu
        :model-value="vulnerabilities"
        create-item="always"
        multiple
        class="w-full"
        icon="i-lucide-bug"
        placeholder="Select the CVEs to use"
        :items="vulnerabilityOptions"
        value-key="id"
        label-key="cve"
        size="xl"
        @update:model-value="
          (value) => {
            vulnerabilities = value;
            $emit('update-vulnerabilities', vulnerabilities);
          }
        "
        @create="createVulnerability"
      >
        <template #trailing>
          <UIcon
            v-if="vulnerabilities.length === 0"
            class="group-data-[state=open]:rotate-180 transition-transform duration-200"
            name="i-lucide-chevron-down"
          />
          <UButton
            v-else
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            size="sm"
            @click="vulnerabilities = []"
          />
        </template>
      </USelectMenu>
    </UFormField>
  </div>
</template>

<script setup lang="ts">
import * as z from "zod";

const props = defineProps<{
  api: object;
  required: boolean;
}>();
const emit = defineEmits<{
  "update-vulnerabilities": [newVulnerabilities: Array<number>];
}>();

const validate = useValidation();
const toast = useToast();
const vulnerabilities = ref([]);
const vulnerabilityOptions = ref([]);
const schema = z.object({
  cve: validate.cve(),
});

function loadVulnerabilities() {
  props.api.list("parameters/vulnerabilities/", {}, true).then((response) => {
    vulnerabilityOptions.value = response.items;
  });
}

function createVulnerability(value: string) {
  try {
    schema.parse({ cve: value });
  } catch {
    toast.add({
      title: "Error",
      description: "Invalid new CVE value",
      color: "error",
    });
    return;
  }
  props.api
    .create("parameters/vulnerabilities/", { cve: value }, {}, "Vulnerability")
    .then((response) => {
      vulnerabilityOptions.value.push(response);
      vulnerabilities.value.push(response.id);
      emit("update-vulnerabilities", vulnerabilities.value);
    });
}

watch(
  () => props.required,
  () =>
    props.required && vulnerabilityOptions.value.length === 0
      ? loadVulnerabilities()
      : null,
);
</script>
