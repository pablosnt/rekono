<template>
  <!-- TODO: Migrate all usages of v-autocomplete to this custom implementation -->
  <!-- TODO: Search doesn't work well because of the getTitle() -->
  <v-autocomplete
    v-model="model"
    auto-select-first
    :items="collection !== null ? collection : Object.keys(definition)"
    :chips="chips"
    :item-name="itemName"
  >
    <template #prepend-inner>
      <v-avatar
        v-if="
          !chips && model && !enforceIcon && prependInner && !model.reference
        "
        v-bind="properties(model, true)"
        variant="text"
      />
      <BaseButton
        v-if="
          !chips &&
          model &&
          !enforceIcon &&
          prependInner &&
          (model.image || model.icon) &&
          model.reference
        "
        :link="model.reference"
        :avatar="properties(model, true).image"
        new-tab
      />
      <v-icon
        v-if="(!model || enforceIcon || !prependInner) && icon"
        :icon="icon"
        :color="iconColor"
      />
    </template>
    <template #item="{ props: itemProps, item }">
      <v-list-item v-bind="itemProps" :title="getTitle(item.raw)">
        <template #prepend>
          <v-avatar
            v-if="properties(item.raw).icon || properties(item.raw).image"
            v-bind="properties(item.raw)"
            variant="text"
          />
        </template>
      </v-list-item>
    </template>
    <template #prepend>
      <slot name="prepend" />
    </template>
    <template #selection="{ item }">
      <p>{{ getTitle(item.raw) }}</p>
    </template>
    <template #append>
      <slot name="append" />
    </template>
    <template v-if="chips" #chip="{ props: itemProps, item }">
      <v-chip v-bind="itemProps" :text="getTitle(item.raw)" closable>
        <template #prepend>
          <v-avatar
            v-if="properties(item.raw).icon || properties(item.raw).image"
            v-bind="properties(item.raw)"
            variant="text"
          />
        </template>
      </v-chip>
    </template>
  </v-autocomplete>
</template>

<script setup lang="ts">
const props = defineProps({
  definition: { type: Object, required: false, default: null },
  collection: { type: Array, required: false, default: null },
  itemTitle: { type: String, required: false, default: undefined },
  title: { type: Function, required: false, default: (value) => value },
  icon: { type: String, required: false, default: undefined },
  enforceIcon: { type: Boolean, required: false, default: false },
  iconColor: { type: String, required: false, default: undefined },
  chips: { type: Boolean, required: false, default: false },
});
const model = defineModel();
const prependInner = ref(true);

function getTitle(value: string | object): string {
  return props.itemTitle ? value[props.itemTitle] : props.title(value);
}

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
      icon: !metadata.icon
        ? props.icon
        : metadata.icon.substring(0, 4) === "mdi-"
          ? metadata.icon
          : undefined,
      image:
        metadata.icon && metadata.icon.substring(0, 4) !== "mdi-"
          ? metadata.icon
          : undefined,
      color: metadata.color ? metadata.color : props.iconColor,
    };
  } else {
    if (updatePrependInner) {
      prependInner.value = false;
    }
    return {};
  }
}
</script>
