<template>
  <BaseButton
    icon
    hover
    :tooltip="item.liked ? 'Dislike' : 'Like'"
    @click.prevent.stop="submit()"
  >
    <template #icon>
      <v-badge floating :content="utils.displayNumber(item.likes)">
        <v-icon
          :icon="item.liked ? 'mdi-heart' : 'mdi-heart-outline'"
          color="red"
        />
      </v-badge>
    </template>
  </BaseButton>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  item: Object,
});
const emit = defineEmits(["reload"]);
const utils = useUtils();
function submit(): void {
  let request = null;
  if (props.item.liked) {
    request = props.api.remove(props.item.id, "like/");
  } else {
    request = props.api.create({}, props.item.id, "like/");
  }
  request.then(() => {
    emit("reload", false);
  });
}
</script>
