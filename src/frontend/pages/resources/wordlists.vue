<template>
    <MenuResources>
        <Dataset :api="api"
            :filtering="filtering"
            @load-data="(data) => wordlists = data"
        >
            <template v-slot:data>
                <v-container fluid>
                    <v-row dense>
                        <v-col v-for="wordlist in wordlists" :key="wordlist.id" cols="6">
                            <v-card :title="wordlist.name"
                                elevation="4"
                                class="mx-auto"
                                density="compact"
                                hover
                            >
                                <!-- TODO: trigger actions -->
                                <template v-slot:append>
                                    <span class="me-3"/>
                                    <v-chip v-if="wordlist.size" color="red">
                                        <v-icon icon="mdi-counter" start/>
                                        {{ wordlist.size < 1000 ? wordlist.size : Math.floor(wordlist.size/1000).toString() + 'k' }}  Words
                                    </v-chip>
                                    <span class="me-3"/>
                                    <v-chip>
                                        <v-icon v-if="wordlist.type === 'Subdomain'" icon="mdi-routes" start/>
                                        <p v-if="wordlist.type === 'Endpoint'"><strong>/</strong><span class="me-1"/></p>
                                        {{ wordlist.type }}
                                    </v-chip>
                                    <span class="me-3"/>
                                    <v-chip v-if="wordlist.owner" color="primary" :variant="wordlist.owner.id === user.user ? 'flat' : 'tonal'">
                                        <v-icon icon="mdi-at" start/>
                                        {{ wordlist.owner.username }}
                                    </v-chip>
                                    <v-chip v-if="!wordlist.owner">Default</v-chip>
                                    <span class="me-3"/>
                                    <v-btn v-if="user.role !== 'Reader'"
                                        icon
                                        color="medium-emphasis"
                                        variant="text"
                                        hover
                                    >
                                        <v-badge floating :content="wordlist.likes < 1000 ? wordlist.likes : Math.floor(wordlist.likes/1000).toString() + 'k'">
                                            <v-icon :icon="wordlist.liked ? 'mdi-heart' : 'mdi-heart-outline'" color="red"/>
                                        </v-badge>
                                        <v-tooltip activator="parent" :text="wordlist.liked ? 'Dislike' : 'Like'"/>
                                    </v-btn>
                                </template>
                            </v-card>
                        </v-col>
                    </v-row>
                </v-container>
            </template>
        </Dataset>
    </MenuResources>
</template>


<script setup lang="ts">
    definePageMeta({layout: false})
    defineEmits(['loadData'])
    const user = userStore()
    const enums = useEnums()
    const wordlists = ref([])
    const api = ref(useApi('/api/wordlists/', true, true, false, 'Wordlist'))
    const filtering = ref([
        {
            type: 'combobox',
            label: 'Type',
            icon: 'mdi-routes',
            collection: enums.wordlists,
            key: 'type',
            value: null
        },
        {
            type: 'switch',
            label: 'Mine',
            color: 'blue',
            cols: 1,
            key: 'owner',
            trueValue: user.user,
            falseValue: null,
            value: null
        },
        {
            type: 'switch',
            label: 'Likes',
            color: 'red',
            cols: 1,
            key: 'like',
            trueValue: true,
            falseValue: null,
            value: null
        },
        {
            type: 'combobox',
            label: 'Sort',
            icon: 'mdi-sort',
            collection: ['id', 'name', 'type', 'size', 'likes_count'],
            fieldValue: 'id',
            fieldTitle: 'name',
            key: 'ordering',
            value: 'id'
        }
    ])
</script>
