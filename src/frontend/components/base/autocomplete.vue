<template>
  <!-- TODO: Migrate all usages of v-autocomplete to this custom implementation -->
  <v-autocomplete
    v-model="model"
    auto-select-first
    :items="collection !== null ? collection : Object.keys(definition)"
    :chips="chips"
  >
    <template #prepend-inner>
      <v-icon
        v-if="!chips && model && !enforceIcon && prependInner"
        v-bind="properties(model, true)"
      />
      <v-icon
        v-if="(!model || enforceIcon || !prependInner) && icon"
        :icon="icon"
        :color="iconColor"
      />
    </template>
    <template #item="{ props: itemProps, item }">
      <v-list-item v-bind="itemProps" :title="title(item.raw)">
        <template #prepend>
          <v-icon
            v-if="properties(item.raw).icon"
            v-bind="properties(item.raw)"
          />
        </template>
      </v-list-item>
    </template>
    <template #selection="{ item }">
      <p>{{ title(item.raw) }}</p>
    </template>
    <template v-if="chips" #chip="{ props: itemProps, item }">
      <v-chip v-bind="itemProps" :text="title(item.raw)" closable>
        <template #prepend>
          <v-icon
            v-if="properties(item.raw).icon"
            v-bind="properties(item.raw)"
          />
        </template>
      </v-chip>
    </template>
  </v-autocomplete>
</template>

<script setup lang="ts">
const props = defineProps({
  definition: {
    type: Object,
    required: false,
    default: null,
  },
  collection: {
    type: Array,
    required: false,
    default: null,
  },
  title: {
    type: Function,
    required: false,
    default: (value) => value,
  },
  icon: {
    type: String,
    required: false,
    default: undefined,
  },
  enforceIcon: {
    type: Boolean,
    required: false,
    default: false,
  },
  iconColor: {
    type: String,
    required: false,
    default: undefined,
  },
  chips: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const model = defineModel();
const prependInner = ref(true);

function properties(item: object, updatePrependInner: boolean = false): object {
  const metadata =
    item.icon !== undefined || item.color !== undefined
      ? item
      : props.definition
        ? props.definition[item]
        : undefined;
  if (metadata !== undefined) {
    if (updatePrependInner) {
      prependInner.value = true;
    }
    return {
      icon: metadata.icon ? metadata.icon : props.icon,
      color: metadata.color,
    };
  } else {
    if (updatePrependInner) {
      prependInner.value = false;
    }
    return {};
  }
}
</script>
