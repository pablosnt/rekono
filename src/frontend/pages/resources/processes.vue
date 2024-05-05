<template>
    <MenuResources>
        <Dataset :api="api"
            :filtering="filtering"
            ordering="id"
            @load-data="(data) => processes = data"
        >
            <template v-slot:data>
                <v-container fluid>
                    <v-row dense>
                        <v-col v-for="process in processes" :key="process.id" cols="4">
                            <v-card :title="process.name"
                                elevation="4"
                                class="mx-auto"
                                density="compact"
                                hover
                            >
                                <v-card-text>
                                    <p>{{ process.description }}</p>
                                    <div v-if="process.tags.length > 0" class="d-flex flex-row justify-center ga-2">
                                        <v-divider class="mt-4 mb-4"/>
                                        <v-chip v-for="tag in process.tags" size="small">
                                            {{ tag }}
                                        </v-chip>
                                    </div>
                                </v-card-text>

                                <template v-slot:append>
                                    <v-chip v-if="process.steps" color="red">
                                        <v-icon icon="mdi-rocket" start/>
                                        {{ process.steps.length }} Steps
                                    </v-chip>
                                    <span class="me-3"/>
                                    <v-chip v-if="process.owner" color="primary" :variant="process.owner.id === user.id ? 'flat' : 'tonal'">
                                        <v-icon icon="mdi-at" start/>
                                        {{ process.owner.username }}
                                    </v-chip>
                                    <v-chip v-if="!process.owner">Default</v-chip>
                                </template>

                                <!-- TODO: Open dialog on click to show the step's details -->
                                <v-card-actions>
                                    <!-- TODO: trigger actions -->
                                    <v-btn hover icon size="large">
                                        <v-icon icon="mdi-play" color="green"/>
                                        <v-tooltip activator="parent" text="Run"/>
                                    </v-btn>
                                    <v-spacer/>
                                    <v-btn icon
                                        color="medium-emphasis"
                                        hover
                                    >
                                        <v-badge floating :content="process.likes < 1000 ? process.likes : Math.floor(process.likes/1000).toString() + 'k'">
                                            <v-icon :icon="process.liked ? 'mdi-heart' : 'mdi-heart-outline'" color="red"/>
                                        </v-badge>
                                        <v-tooltip activator="parent" :text="process.liked ? 'Dislike' : 'Like'"/>
                                    </v-btn>
                                </v-card-actions>
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
    const processes = ref([])
    const api = ref(useApi('/api/processes/', true, true, false, 'Process'))
    let tools = []
    await useApi('/api/tools/', true, false, false, 'Tool').list({}, true)
        .then((response) => { tools = response.items })
    const filtering = ref([
        {
            type: 'combobox',
            label: 'Tool',
            icon: 'mdi-rocket',
            collection: tools,
            fieldValue: 'id',
            fieldTitle: 'name',
            key: 'tool',
            value: null
        },
        {
            type: 'combobox',
            label: 'Stage',
            icon: 'mdi-stairs',
            collection: Object.entries(enums.stages).map(([k, v]) => { v.name = k; return v }),
            fieldValue: 'id',
            fieldTitle: 'name',
            key: 'stage',
            value: null
        },
        {
            type: 'text',
            label: 'Tag',
            icon: 'mdi-tag',
            key: 'tag',
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
        }
    ])
</script>