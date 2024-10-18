<template>
  <v-chip
    v-if="note.public"
    prepend-icon="mdi-arrow-decision"
    color="red"
    :variant="!note.forked ? 'tonal' : 'flat'"
    :disabled="note.forked || note.owner.id === user.user"
    @click="
      useApi('/api/notes/', true)
        .create({}, note.id, 'fork/')
        .then((response) => router.push(`/notes/${response.id}`))
    "
    >{{
      note.forks.length < 1000
        ? note.forks.length
        : Math.floor(note.forks.length / 1000).toString() + "k"
    }}
    Forks</v-chip
  >
</template>

<script setup lang="ts">
defineProps({ note: Object });
const user = userStore();
const router = useRouter();
</script>
