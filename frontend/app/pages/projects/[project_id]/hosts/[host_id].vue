<template>
  <FindingsSingle
    :loading="loading"
    :icon="osConfig?.icon || 'i-lucide-server'"
    :icon-color="osConfig?.color"
    :api="api"
    :title="host?.domain || host?.ip || ''"
    :finding="host"
    entity-name="Host"
    is-asset
    fix-verb="Discard"
    @update="fetch()"
  >
    <template #metadata>
      <div
        v-if="host?.domain && host?.ip"
        class="flex items-center gap-2 flex-wrap"
      >
        <span class="text-muted">IP:</span>
        <span class="text-base">{{ host.ip }}</span>
        <UButton
          icon="i-lucide-copy"
          color="neutral"
          variant="ghost"
          size="xs"
          aria-label="Copy IP address"
          @click="copyText(host.ip)"
        />
      </div>
      <div v-if="host?.os" class="flex items-center gap-2 flex-wrap">
        <span class="text-muted">OS:</span>
        <span class="text-base">{{ host.os }}</span>
      </div>
      <div
        v-if="host?.country && !(host?.latitude && host?.longitude)"
        class="flex items-center gap-2 flex-wrap"
      >
        <span class="text-muted">Country:</span>
        <div class="flex items-center gap-2">
          <UIcon
            :name="
              host.country ? `cif:${host.country.toLowerCase()}` : undefined
            "
          />
          <span class="text-base">{{ host.country }}</span>
        </div>
      </div>
      <div
        v-if="host?.city && !(host?.latitude && host?.longitude)"
        class="flex items-center gap-2 flex-wrap"
      >
        <span class="text-muted">City:</span>
        <span class="text-base">{{ host.city }}</span>
      </div>
    </template>
    <template #custom-skeleton>
      <SkeletonCards
        class="lg:grid-cols-2"
        :count="2"
        :lines="10"
        variant="outline"
        :leading="false"
      >
        <template #description="{ card }">
          <span v-if="card === 2" />
        </template>
        <template #default="{ card }">
          <SkeletonMetrics
            v-if="card === 2"
            :height="200"
            class="flex-2 min-w-80"
          />
        </template>
      </SkeletonCards>
      <SkeletonCards
        v-if="integrations.virustotal.integration?.enabled"
        class="sm:grid-cols-1 lg:grid-cols-1"
        :count="1"
        :lines="0"
        variant="outline"
        :leading="false"
      >
        <div class="flex flex-wrap items-center gap-8 w-full">
          <UCard class="flex-1 min-w-48 bg-neutral/10">
            <div class="flex flex-col items-center">
              <USkeleton class="h-15 w-28" />
              <USkeleton class="h-5 w-32 mt-2" />
            </div>
          </UCard>
          <SkeletonMetrics :height="200" class="flex-2 min-w-80" />
        </div>
      </SkeletonCards>
    </template>
    <template #custom>
      <div
        v-if="host?.whois || (host?.latitude && host?.longitude)"
        class="flex flex-wrap items-start gap-8 w-full"
      >
        <UPageCard
          v-if="host?.whois"
          title="WHOIS"
          variant="outline"
          class="w-full sm:flex-1"
          :ui="{ root: 'overflow-x-auto' }"
        >
          <span class="whitespace-pre-wrap font-mono">{{ host.whois }}</span>
        </UPageCard>
        <UPageCard
          v-if="host?.latitude && host?.longitude"
          title="Geolocation"
          :description="host?.city ? host?.city : host?.country"
          variant="outline"
          class="w-full sm:flex-1"
        >
          <template v-if="host?.country && host?.city" #description>
            <div class="flex items-center gap-2">
              <UIcon
                :name="
                  host?.country
                    ? `cif:${host.country.toLowerCase()}`
                    : undefined
                "
              />
              <span class="text-base">{{ host.city }}</span>
            </div>
          </template>
          <FindingsHostsLocations :hosts="[host]" />
        </UPageCard>
      </div>
      <UPageCard
        v-if="
          (host?.total_analysis > 0 || host?.reputation !== 0) &&
          integrations.virustotal.integration?.enabled
        "
        title="Malware Analysis"
        variant="outline"
      >
        <div class="flex flex-wrap items-center gap-8 w-full">
          <UCard
            v-if="host?.total_analysis > 0 || host?.reputation !== 0"
            :class="
              host.reputation > 0
                ? 'bg-success/10 ring-success/30'
                : host.reputation < 0
                  ? 'bg-error/10 ring-error/30'
                  : 'bg-neutral/10'
            "
            class="flex-1 min-w-48 text-center"
          >
            <p
              :class="
                host.reputation > 0
                  ? 'text-success'
                  : host.reputation < 0
                    ? 'text-error'
                    : 'text-muted'
              "
              class="text-6xl font-bold tabular-nums"
            >
              {{ host.reputation > 0 ? "+" : "" }}{{ host.reputation }}
            </p>
            <p class="text-muted mt-2">Reputation Score</p>
          </UCard>
          <FindingsHostsMalware :host="host" />
        </div>
      </UPageCard>
      <UPageCard
        v-if="host?.port.length > 0"
        variant="outline"
        :ui="{ header: 'w-full', container: 'min-w-0' }"
      >
        <FindingsPorts
          :host="host.id"
          :link-to-original-page="`/projects/${route.params.project_id}/ports?host=${host.id}`"
        />
      </UPageCard>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
import { hostOS } from "~/constants";
import { useIntegrationsStore } from "~/store/integrations";

const api = useApi("/api/hosts/");
const route = useRoute();
const integrations = useIntegrationsStore();
const host = ref();
const osConfig = ref();
const loading = ref(true);

function fetch(initial: boolean = false) {
  loading.value = true;
  (initial ? api.getOrError : api.get)(`${route.params.host_id}/`)
    .then((response) => {
      host.value = response;
      osConfig.value = hostOS.find((h) => h.value === host.value.os_type);
    })
    .finally(() => {
      loading.value = false;
    });
}

onMounted(() => {
  fetch(true);
  integrations.fetchVirusTotal();
});
</script>
