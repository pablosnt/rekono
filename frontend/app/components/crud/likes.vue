<template>
  <UButton
    :color="liked ? 'primary' : 'neutral'"
    :variant="variant || 'subtle'"
    :size="size || 'md'"
    class="gap-2"
    @click.stop="toggleLike()"
  >
    <UIcon name="i-lucide-heart" :class="liked ? 'fill-current' : ''" />
    <span>{{ count }}</span>
  </UButton>
</template>

<script setup lang="ts">
const props = defineProps<{
  itemId: number;
  endpoint: string;
  liked: boolean;
  count: number;
  variant?: string;
  size?: string;
}>();

const emit = defineEmits<{
  update: [liked: boolean, count: number];
}>();

async function toggleLike() {
  const api = useApi(`${props.endpoint}${props.itemId}/like/`);
  const method = props.liked ? api.remove : api.create;
  method("", {}).then(() => {
    const newLiked = !props.liked;
    const newCount = props.count + (newLiked ? 1 : -1);
    emit("update", newLiked, newCount);
  });
}
</script>
