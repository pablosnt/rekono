<template>
    <v-btn icon hover color="medium-emphasis" variant="text" @click.stop="submit()">
        <v-badge floating :content="item.likes < 1000 ? item.likes : Math.floor(item.likes/1000).toString() + 'k'">
            <v-icon :icon="item.liked ? 'mdi-heart' : 'mdi-heart-outline'" color="red"/>
        </v-badge>
        <v-tooltip activator="parent" :text="item.liked ? 'Dislike' : 'Like'"/>
    </v-btn>
</template>

<script setup lang="ts">
    const props = defineProps({
        api: Object,
        item: Object
    })
    const emit = defineEmits(['reload'])
    function submit() {
        let request = null
        if (props.item.liked) {
            request = props.api.remove(props.item.id, 'like/')
        } else {
            request = props.api.create({}, props.item.id, 'like/')
        }
        request.then(() => { emit('reload', false) })
    }
</script>