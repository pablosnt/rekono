<template>
    <DialogDefault :title="edit ? 'Edit Wordlist' : 'New Wordlist'"
        :loading="loading"
        @close-dialog="loading = false; $emit('closeDialog')"
    >
        <template v-slot>
            <FormWordlist :api="api"
                :edit="edit ? edit : null"
                @loading="(value) => loading = value"
                @completed="loading = false; $emit('completed'); $emit('closeDialog')"
            />
        </template>
    </DialogDefault>
</template>

<script setup lang="ts">
    defineProps({
        api: Object,
        edit: Object
    })
    const emit = defineEmits(['closeDialog', 'completed'])
    const loading = ref(false)
</script>