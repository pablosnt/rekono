<template>
    <MenuResources>
        <Dataset ref="dataset"
            :api="api"
            :filtering="filtering"
            ordering="id"
            :add="DialogProcess"
            :addFullscreen="true"
            @load-data="(data) => processes = data"
        >
            <template v-slot:data>
                <v-container v-if="processes !== null" fluid>
                    <v-row v-if="processes.length === 0" justify="center" dense>
                        <v-empty-state icon="mdi-robot" title="There are no processes"/>
                    </v-row>
                    <v-row dense>
                        <v-col v-for="process in processes" :key="process.id" cols="4">
                            <v-dialog width="100%" fullscreen>
                                <template v-slot:activator="{ props: activatorProps }">
                                    <ShowProcess :api="api" :process="process" :tools="tools" :details="false" @reload="(value) => dataset.loadData(value)" v-bind="activatorProps"/>
                                </template>
                                <template v-slot:default="{ isActive }">
                                    <ShowProcess :api="api" :process="process" :tools="tools" :details="true" @reload="(value) => dataset.loadData(value)" @close-dialog="isActive.value = false"/>
                                </template>
                            </v-dialog>
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
    const DialogProcess = resolveComponent('DialogProcess')
    const dataset = ref(null)
    const processes = ref(null)
    const api = ref(useApi('/api/processes/', true, 'Process'))
    let tools = ref([])
    const filtering = ref([
        {
            type: 'autocomplete',
            label: 'Stage',
            icon: 'mdi-stairs',
            cols: 2,
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
        },
        {
            type: 'autocomplete',
            label: 'Sort',
            icon: 'mdi-sort',
            cols: 2,
            collection: ['id', 'name', 'likes_count'],
            fieldValue: 'id',
            fieldTitle: 'name',
            key: 'ordering',
            value: 'id'
        }
    ])
    useApi('/api/tools/', true, 'Tool')
        .list({}, true)
        .then((response) => {
            tools.value = response.items
            filtering.value = [
                {
                    type: 'autocomplete',
                    label: 'Tool',
                    icon: 'mdi-rocket',
                    collection: tools.value,
                    fieldValue: 'id',
                    fieldTitle: 'name',
                    key: 'tool',
                    value: null
                }
            ].concat(filtering.value)
        })
</script>