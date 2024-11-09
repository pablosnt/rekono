<template>
  <v-btn
    icon
    hover
    color="medium-emphasis"
    variant="text"
    @click.prevent.stop="submit()"
  >
    <v-badge floating :content="utils.displayNumber(item.subscribers.length)">
      <v-icon
        :icon="item.subscribed ? 'mdi-bell-ring' : 'mdi-bell-outline'"
        color="red"
      />
    </v-badge>
    <v-tooltip
      activator="parent"
      :text="item.subscribed ? 'Unsubscribe' : 'Subscribe'"
    />
  </v-btn>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  item: Object,
});
const emit = defineEmits(["reload"]);
const utils = useUtils();
function submit() {
  let request = null;
  if (props.item.subscribed) {
    request = props.api.remove(props.item.id, "subscription/");
  } else {
    request = props.api.create({}, props.item.id, "subscription/");
  }
  request.then(() => {
    emit("reload");
  });
}
</script>
