<template>
  <v-card
    :title="item.item"
    elevation="3"
    class="mx-auto"
    density="compact"
    :hover="hover"
  >
    <template v-if="item.value !== null || item.mode === 'Monitor'" #subtitle>
      <p v-if="item.mode === 'Monitor'">
        Monitor {{ enums.alertItems[item.item].monitor }}
        {{ item.item }}
      </p>
      <p v-if="item.value !== null">
        <span class="text-medium-emphasis"
          >{{ enums.alertItems[item.item].filter.charAt(0).toUpperCase()
          }}{{ enums.alertItems[item.item].filter.slice(1) }} == </span
        >'{{ item.value }}'
      </p>
    </template>
    <template #prepend>
      <BaseButton
        hover
        :icon="enums.alertModes[item.mode].icon"
        icon-color="green"
        :tooltip="item.mode"
      />
    </template>
    <template #append>
      <v-switch
        :model-value="item.enabled"
        color="success"
        class="mt-5 mr-3"
        @click.prevent.stop="
          item.enabled
            ? api.remove(item.id, 'enable/').then(() => {
                item.enabled = false;
                _alert(
                  `Alert '${item.mode} ${item.item}' has been disabled`,
                  'warning',
                );
              })
            : api.create({}, item.id, 'enable/').then((response) => {
                item = response;
                _alert(
                  `Alert '${item.mode} ${item.item}' has been enabled`,
                  'success',
                );
              })
        "
      />
      <UtilsOwner :entity="item" />
    </template>
    <v-card-actions>
      <AlertSubscribe :api="api" :item="alert" @reload="$emit('reload')" />
      <v-spacer />
      <UtilsDeleteButton
        :id="item.id"
        :api="api"
        :text="`Alert '${item.mode} ${item.item}' will be removed`"
        icon="mdi-trash-can"
        @completed="$emit('reload')"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  alert: Object,
  hover: { type: Boolean, required: false, default: false },
});
defineEmits(["reload"]);
const enums = useEnums();
const _alert = ref(useAlert());
const item = ref(props.alert);
</script>
