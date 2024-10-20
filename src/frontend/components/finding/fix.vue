<template>
  <v-btn
    v-if="
      finding.triage_status === undefined ||
      !['False Positive', 'Won\'t Fixed'].includes(finding.triage_status)
    "
    class="text-none"
    variant="text"
  >
    <v-chip
      color="green"
      :disabled="finding.auto_fixed"
      :variant="finding.is_fixed ? 'tonal' : 'flat'"
      :closable="finding.is_fixed && !finding.auto_fixed"
      @click="
        finding.is_fixed
          ? null
          : api.create({}, finding.id, 'fix/').then(() => $emit('change'))
      "
    >
      <template v-if="finding.is_fixed && !finding.auto_fixed" #close>
        <v-icon
          icon="mdi-close-circle"
          @click.stop="
            api.remove(finding.id, 'fix/').then(() => $emit('change'))
          "
        />
      </template>
      <p v-if="finding.is_fixed && finding.fixed_by">
        {{ assetSyntax ? "Outscoped" : "Fixed" }} by @{{
          finding.fixed_by.username
        }}
      </p>
      <template v-if="finding.is_fixed && finding.auto_fixed">
        <v-icon icon="mdi-robot" start />
        <p>{{ assetSyntax ? "Auto-Outscoped" : "Auto-Fixed" }}</p>
      </template>
      <p v-if="!finding.is_fixed">{{ assetSyntax ? "OUTSCOPE" : "FIX" }}</p>
    </v-chip>
    <v-tooltip
      v-if="finding.is_fixed && finding.fixed_date"
      activator="parent"
      :text="new Date(finding.fixed_date).toDateString()"
    />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  finding: Object,
  assetSyntax: { type: Boolean, required: false, default: false },
});
defineEmits(["change"]);
</script>
