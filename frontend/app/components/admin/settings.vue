<template>
  <CrudPage
    :config="{
      entityNamePlural: 'Settings',
      entityName: 'Settings',
      canRead: userStore.is_admin,
      canEdit: false,
      canDelete: false,
      canCreate: false,
      showAccessDeniedError: false,
    }"
  >
    <template #content>
      <UProgress :class="[loading ? 'visible' : 'invisible', 'mb-1']" />
      <CrudForm
        ref="form"
        :api="api"
        :config="config"
        :entity="settings"
        grid-cols="grid-cols-1 md:grid-cols-2"
        @submit="
          (data) => {
            settings = data;
            valid = false;
          }
        "
        @validation-change="(isValid) => (valid = isValid)"
        @new-loading="(newLoading) => (loading = newLoading)"
      />
      <div class="mt-8 flex justify-end">
        <UButton
          :disabled="!valid"
          :loading="loading"
          label="Save"
          @click="
            loading = true;
            form.submit();
          "
        />
      </div>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import * as z from "zod";

const api = useApi("/api/settings/");
const userStore = useUserStore();
const validation = useValidation();
const form = ref();
const settings = ref();
const loading = ref(false);
const valid = ref(false);
const config = ref({
  entityName: "Settings",
  editFormFields: [
    {
      key: "all_proxy",
      label: "ALL_PROXY",
      type: "text",
      placeholder: "proxy.example.com",
      required: false,
      inputMode: "url",
    },
    {
      key: "http_proxy",
      label: "HTTP_PROXY",
      type: "text",
      placeholder: "http://proxy.example.com",
      required: false,
      inputMode: "url",
    },
    {
      key: "https_proxy",
      label: "HTTPS_PROXY",
      type: "text",
      placeholder: "https://proxy.example.com",
      required: false,
      inputMode: "url",
    },
    {
      key: "ftp_proxy",
      label: "FTP_PROXY",
      type: "text",
      placeholder: "ftp://proxy.example.com",
      required: false,
      inputMode: "url",
    },
    {
      key: "no_proxy",
      label: "NO_PROXY",
      type: "text",
      placeholder: ".internal.example.com",
      required: false,
      inputMode: "url",
    },

    {
      key: "max_uploaded_file_mb",
      label: "Max file size in MB",
      type: "number",
      required: true,
      hint: "Max file size allowed to be uploaded in MB",
      icon: "i-lucide-cloud-upload",
      min: 128,
      max: 3072,
    },
    {
      key: "auto_fix_findings",
      label:
        "Automatically fix findings when they are no longer detected by the same scan",
      type: "checkbox",
      required: true,
      icon: "i-lucide-bug-off",
    },
  ],
  editFormSchema: z.object({
    all_proxy: validation
      .target_regex("all_proxy", false, 300)
      .or(z.literal("")),
    http_proxy: validation
      .target_regex("http_proxy", false, 300)
      .or(z.literal("")),
    https_proxy: validation
      .target_regex("https_proxy", false, 300)
      .or(z.literal("")),
    ftp_proxy: validation
      .target_regex("ftp_proxy", false, 300)
      .or(z.literal("")),
    no_proxy: validation.target_regex("no_proxy", false, 300).or(z.literal("")),
    max_uploaded_file_mb: z.number().min(128).max(3072),
    auto_fix_findings: z.boolean(),
  }),
});

function fetch() {
  loading.value = true;
  api
    .get("1/")
    .then((response) => {
      settings.value = response;
    })
    .then(() => {
      loading.value = false;
    });
}

onMounted(() => {
  fetch();
});
</script>
