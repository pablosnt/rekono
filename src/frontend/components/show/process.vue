<template>
    <v-card :title="process.name"
        elevation="4"
        class="mx-auto"
        density="compact"
        hover
    >
        <template v-slot:append>
            <v-chip v-if="process.steps" color="red">
                <v-icon icon="mdi-rocket" start/>
                {{ process.steps.length }} Steps
            </v-chip>
            <span class="me-3"/>
            <v-chip v-if="process.owner" color="primary" :variant="process.owner.id === user.user ? 'flat' : 'tonal'">
                <v-icon icon="mdi-at" start/>
                {{ process.owner.username }}
            </v-chip>
            <v-chip v-if="!process.owner">Default</v-chip>
        </template>

        <v-card-text class="overflow-auto">
            <p>{{ process.description }}</p>
            <div v-if="details && process.tags.length > 0">
                <v-divider class="mt-4 mb-4"/>
                <div class="d-flex flex-row justify-center">
                    <v-chip-group selected-class="v-chip">
                        <v-chip v-for="tag in process.tags" size="small">
                            {{ tag }}
                        </v-chip>
                    </v-chip-group>
                    </div>
            </div>
            <div v-if="details && process.steps.length > 0">
                <v-stepper v-model="stage" editable alt-labels hide-actions flat>
                    <v-stepper-header>
                        <template v-for="s in stages" :key="s">
                            <v-divider v-if="s !== stages[0]"/>
                            <v-stepper-item :title="s" :color="enums.stages[s].color" :edit-icon="enums.stages[s].icon"/>
                        </template>
                    </v-stepper-header>
                    <v-stepper-window>
                        <template v-for="step in process.steps" :key="step.id">
                            <v-banner v-if="step.configuration.stage === stages[stage]"
                                :avatar="step.configuration.tool.icon"
                                :text="step.configuration.tool.name + '  -  ' + step.configuration.name"
                                :stacked="false"
                            >
                                <template v-slot:actions>
                                    <v-btn icon="mdi-trash-can-outline" color="red" hover/>
                                    <v-btn icon="mdi-open-in-new"
                                        color="medium-emphasis"
                                        target="_blank"
                                        :href="step.configuration.tool.reference ? step.configuration.tool.reference : null"
                                        hover
                                    />
                                </template>
                            </v-banner>
                        </template>
                    </v-stepper-window>
                </v-stepper>
            </div>
        </v-card-text>

        <v-card-actions v-if="user.role !== 'Reader'">
            <!-- TODO: trigger actions -->
            <v-btn hover icon size="large">
                <v-icon icon="mdi-play" color="green"/>
                <v-tooltip activator="parent" text="Run"/>
            </v-btn>
            <v-btn v-if="(process.owner !== null && process.owner.id === user.user) || user.role === 'Admin'" hover icon size="large">
                <v-icon icon="mdi-rocket" color="blue-grey"/>
                <v-tooltip activator="parent" text="Add new step"/>
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
            <v-speed-dial v-if="(process.owner !== null && process.owner.id === user.user) || user.role === 'Admin'" transition="scale-transition" location="bottom end" @click.native.stop>
                <template v-slot:activator="{ props: activatorProps }">
                    <v-btn v-bind="activatorProps"
                        size="large"
                        color="grey"
                        icon="mdi-cog"
                    />
                    <v-tooltip activator="parent" text="Settings"/>
                </template>
                <v-btn key="1" icon="mdi-pencil" color="black"/>
                <v-btn key="2" icon="mdi-trash-can-outline" color="red"/>
            </v-speed-dial>
        </v-card-actions>
    </v-card>
</template>

<script setup lang="ts">
    const props = defineProps({
        api: Object,
        process: Object,
        details: Boolean
    })
    const user = userStore()
    const stage = ref(null)
    const enums = ref(useEnums())
    const stages = Object.keys(enums.value.stages).filter((stage) => props.process.steps.filter((step) => step.configuration.stage === stage).length > 0)
</script>