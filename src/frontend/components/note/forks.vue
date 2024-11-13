<template>
  <UtilsCounter
    v-if="note.public"
    :collection="note.forks"
    icon="mdi-arrow-decision"
    :variant="!note.forked ? 'tonal' : 'flat'"
    :disabled="note.forked || note.owner.id === user.user"
    entity="Forks"
    show-zero
    @click.prevent.stop="
      useApi('/api/notes/', true)
        .create({}, note.id, 'fork/')
        .then((response) => router.push(`/notes/${response.id}`))
    "
  />
</template>

<script setup lang="ts">
defineProps({ note: Object });
const user = userStore();
const router = useRouter();
</script>
