<template>
    <MenuResources>
        <Dataset :api="api"
            :filtering="filtering"
            ordering="id"
            @load-data="(data) => tools = data"
        >
            <template v-slot:data>
                <v-container fluid>
                    <v-row dense>
                        <v-col v-for="tool in tools" :key="tool.id" cols="4">
                            <v-card :title="tool.name"
                                :subtitle="'$ ' + tool.command + (tool.script ? ' ' + tool.script : '')"
                                :prepend-avatar="tool.icon"
                                rel="noopener"
                                elevation="4"
                                class="mx-auto"
                                density="compact"
                                hover
                            >
                                <v-card-text>
                                    <template v-for="configuration in tool.configurations">
                                        <div class="d-flex flex-row">
                                            <v-btn v-if="configuration.default"
                                                icon
                                                size="medium"
                                                variant="text"
                                                @click="show = show !== tool.id ? tool.id : null"
                                            >
                                                <p >{{ configuration.name }}</p>
                                                <span class="me-2"/>
                                                <v-icon v-if="tool.configurations.length > 1" :icon="show === tool.id ? 'mdi-chevron-up' : 'mdi-chevron-down'" color="black"/>
                                                <v-tooltip activator="parent" :text="tool.configurations.length > 1 ? 'Configurations' : 'Configuration'"/>
                                            </v-btn>
                                        </div>
                                        <v-expand-transition>
                                            <div v-show="show == tool.id" v-if="!configuration.default">
                                                <p>{{ configuration.name }}</p>
                                            </div>
                                        </v-expand-transition>
                                    </template>
                                    <v-divider class="mt-4 mb-4"/>
                                    <div class="d-flex flex-row justify-center ga-2">
                                        <v-chip v-for="intensity in tool.intensities" size="small" :color="enums.intensities[intensity.value].color">
                                            {{ intensity.value }}
                                        </v-chip>
                                    </div>
                                </v-card-text>

                                <template v-slot:append>
                                    <v-chip v-if="tool.version">
                                        <v-icon icon="mdi-tag" start/>
                                        {{ tool.version }}
                                    </v-chip>
                                    <span class="me-3"/>
                                    <v-btn hover icon variant="text">
                                        <v-icon :icon="tool.is_installed ? 'mdi-check-circle' : 'mdi-close-circle'" :color="tool.is_installed ? 'green' : 'red'"/>
                                        <v-tooltip activator="parent" :text="tool.is_installed ? 'Installed' : 'Tool may have been installed after its last execution attempt'"/>
                                    </v-btn>
                                </template>
                            
                                <v-card-actions>
                                    <!-- TODO: trigger actions -->
                                    <v-btn hover icon size="large">
                                        <v-icon icon="mdi-play" color="green"/>
                                        <v-tooltip activator="parent" text="Run"/>
                                    </v-btn>
                                    <v-btn hover icon size="large">
                                        <v-icon icon="mdi-robot" color="blue-grey"/>
                                        <v-tooltip activator="parent" text="Add to process"/>
                                    </v-btn>
                                    <v-spacer/>
                                    <v-btn icon
                                        color="medium-emphasis"
                                        hover
                                    >
                                        <v-badge floating :content="tool.likes < 1000 ? tool.likes : Math.floor(tool.likes/1000).toString() + 'k'">
                                            <v-icon :icon="tool.liked ? 'mdi-heart' : 'mdi-heart-outline'" color="red"/>
                                        </v-badge>
                                        <v-tooltip activator="parent" :text="tool.liked ? 'Dislike' : 'Like'"/>
                                    </v-btn>
                                    <v-btn icon="mdi-open-in-new"
                                        color="medium-emphasis"
                                        target="_blank"
                                        :href="tool.reference ? tool.reference : null"
                                        hover
                                    />
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
    const tools = ref([])
    const show = ref(null)
    const enums = ref(useEnums())
    const api = ref(useApi('/api/tools/', true, true, false, 'Tool'))
    const filtering = ref([
        {
            type: 'combobox',
            label: 'Stage',
            icon: 'mdi-stairs',
            collection: Object.entries(enums.value.stages).map(([k, v]) => { v.name = k; return v }),
            fieldValue: 'id',
            fieldTitle: 'name',
            key: 'stage',
            value: null
        },
        {
            type: 'combobox',
            label: 'Intensity',
            icon: 'mdi-volume-high',
            collection: Object.entries(enums.value.intensities).map(([k, v]) => { v.name = k; return v }),
            fieldValue: 'id',
            fieldTitle: 'name',
            key: 'intensity',
            value: null
        },
        {
            type: 'switch',
            label: 'Installed',
            color: 'green',
            cols: 2,
            key: 'is_installed',
            trueValue: true,
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
            collection: ['id', 'name', 'command'],
            fieldValue: 'id',
            fieldTitle: 'name',
            key: 'ordering',
            value: 'id'
        }
    ])
</script>