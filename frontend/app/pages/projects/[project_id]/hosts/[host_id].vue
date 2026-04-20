<template>
  <FindingsSingle
    v-if="host"
    :icon="osConfig?.icon || 'i-lucide-server'"
    :icon-color="osConfig?.color"
    :api="api"
    :title="host.domain || host.ip"
    :finding="host"
    entity-name="Host"
    is-asset
    fix-verb="Discard"
    @update="fetch()"
  >
    <!-- TODO: Move this to the FindingsSingle by default and allow disabling it? -->
    <template #post-title>
      <UButton
        icon="i-lucide-copy"
        color="neutral"
        variant="ghost"
        size="xs"
        @click="copy(host.domain || host.ip)"
      />
    </template>
    <template #metadata>
      <div v-if="host.domain && host.ip" class="flex items-center gap-2">
        <span class="text-muted">IP:</span>
        <span class="text-base">{{ host.ip }}</span>
        <UButton
          icon="i-lucide-copy"
          color="neutral"
          variant="ghost"
          size="xs"
          @click="copy(host.ip)"
        />
      </div>
      <div v-if="host.os" class="flex items-center gap-2">
        <span class="text-muted">OS:</span>
        <span class="text-base">{{ host.os }}</span>
      </div>
      <div
        v-if="host.country && !(host.latitude && host.longitude)"
        class="flex items-center gap-2"
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
        v-if="host.city && !(host.latitude && host.longitude)"
        class="flex items-center gap-2"
      >
        <span class="text-muted">City:</span>
        <span class="text-base">{{ host.city }}</span>
      </div>
    </template>
    <template #custom>
      <UPageCard
        v-if="
          (host.total_analysis > 0 || host.reputation !== 0) &&
          virusTotal?.enabled
        "
        title="Malware Analysis"
        variant="outline"
      >
        <div class="flex items-center gap-8 flex-wrap w-full">
          <UCard
            v-if="host.total_analysis > 0 || host.reputation !== 0"
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
          <FindingsHostsMetricsMalware :host="host" />
        </div>
      </UPageCard>
      <div
        v-if="host.whois || (host.latitude && host.longitude)"
        class="flex items-stretch gap-4 flex-wrap w-full"
      >
        <UPageCard
          v-if="host.whois"
          title="WHOIS"
          variant="outline"
          class="flex-1 min-w-150"
        >
          <span class="whitespace-pre-wrap font-mono">{{ host.whois }}</span>
        </UPageCard>
        <UPageCard
          v-if="host.latitude && host.longitude"
          title="Geolocation"
          :description="host.city ? host.city : host.country"
          variant="outline"
          class="flex-1 min-w-150"
        >
          <template v-if="host.country && host.city" #description>
            <div class="flex items-center gap-2">
              <UIcon
                :name="
                  host.country ? `cif:${host.country.toLowerCase()}` : undefined
                "
              />
              <span class="text-base">{{ host.city }}</span>
            </div>
          </template>
          <FindingsHostsMetricsLocations :hosts="[host]" />
        </UPageCard>
      </div>
      <UPageCard v-if="host.port.length > 0" title="Ports" variant="outline">
        <FindingsPorts :host="host.id" />
      </UPageCard>
    </template>
  </FindingsSingle>
</template>

<script setup lang="ts">
import { hostOS } from "~/constants";

definePageMeta({ layout: "project" });

const api = useApi("/api/hosts/");
const route = useRoute();
const toast = useToast();
const host = ref();
const osConfig = ref();
const virusTotal = ref();

function copy(value: string) {
  navigator.clipboard.writeText(value);
  toast.add({ title: `${value} copied to clipboard`, color: "success" });
}

function fetch() {
  api.get(`${route.params.host_id}/`).then((response) => {
    host.value = response;
    osConfig.value = hostOS.find((h) => h.value === host.value.os_type);
  });
  useApi("/api/integrations/")
    .get("5/")
    .then((response) => {
      virusTotal.value = response;
    });
}

onMounted(fetch);
</script>
