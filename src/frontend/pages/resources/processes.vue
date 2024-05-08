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
                            <v-dialog width="auto">
                                <template v-slot:activator="{ props: activatorProps }">
                                    <ShowProcess :api="api" :process="process" :details="false" v-bind="activatorProps"/>
                                </template>
                                <template v-slot:default="{ isActive }">
                                    <ShowProcess :api="api" :process="process" :details="true"/>
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
            type: 'combobox',
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
</script>