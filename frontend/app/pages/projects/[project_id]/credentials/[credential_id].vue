<template>
  <FindingsSingle
    :loading="loading"
    :api="api"
    :title="
      credential?.username || credential?.email || credential?.secret || ''
    "
    :finding="credential"
    entity-name="Credential"
    is-triageable
    fix-verb="Fix"
    @update="fetch()"
  >
    <template #metadata>
      <FindingsMetadataHost :host="credential?.technology?.port?.host" />
      <FindingsMetadataPort :port="credential?.technology?.port" />
      <FindingsMetadataTechnology :technology="credential?.technology" />
      <div
        v-if="credential?.email && credential?.username"
        class="flex items-center gap-2 flex-wrap"
      >
        <span class="text-muted">Email:</span>
        <span class="text-base">{{ credential.email }}</span>
        <UButton
          icon="i-lucide-copy"
          color="neutral"
          variant="ghost"
          size="xs"
          @click="copyText(credential.email)"
        />
      </div>
      <div
        v-if="(credential?.email || credential?.username) && credential?.secret"
        class="flex items-center gap-2 flex-wrap"
      >
        <span class="text-muted">Secret:</span>
        <span class="text-base">{{ credential.secret }}</span>
        <UButton
          icon="i-lucide-copy"
          color="neutral"
          variant="ghost"
          size="xs"
          @click="copyText(credential.email, 'Secret copied to clipboard')"
        />
      </div>
      <div v-if="credential?.context" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">Context:</span>
        <span class="text-base">{{ credential.context }}</span>
      </div>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
const api = useApi("/api/credentials/");
const route = useRoute();
const credential = ref();
const loading = ref(true);

function fetch() {
  loading.value = true;
  api
    .get(`${route.params.credential_id}/`)
    .then((response) => (credential.value = response))
    .finally(() => {
      loading.value = false;
    });
}

onMounted(fetch);
</script>
