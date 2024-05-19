<template>
    <v-card :title="process.name"
        elevation="4"
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
            <v-btn v-if="details" icon="mdi-close"
                variant="text"
                @click="$emit('closeDialog')"
            />
        </template>

        <v-card-text class="overflow-auto">
            <div v-if="!details">
                <p>{{ process.description }}</p>
                <div v-if="process.tags.length > 0">
                    <v-divider class="mt-4 mb-4"/>
                    <v-chip-group selected-class="v-chip">
                        <v-chip v-for="tag in process.tags" size="small">
                            {{ tag }}
                        </v-chip>
                    </v-chip-group>
                </div>
            </div>
            <div v-if="details">
                <FormSteps :process="process"
                    :tools="tools"
                    @reload="() => $emit('reload', false)"
                />
            </div>
        </v-card-text>

        <v-card-actions v-if="user.role !== 'Reader'">
            <v-dialog width="auto">
                <template v-slot:activator="{ props: activatorProps }">
                    <v-btn hover icon size="x-large" v-bind="activatorProps">
                        <v-icon icon="mdi-play-circle" color="green"/>
                        <v-tooltip activator="parent" text="Run"/>
                    </v-btn>
                </template>
                <template v-slot:default="{ isActive }">
                    <DialogTask :process="process" @close-dialog="isActive.value = false"/>
                </template>
            </v-dialog>
            <v-spacer/>
            <ButtonLike :api="api" :item="process" @reload="(value) => $emit('reload', value)"/>
            <v-speed-dial v-if="(process.owner !== null && process.owner.id === user.user) || user.role === 'Admin'" transition="scale-transition" location="bottom end" @click.native.stop>
                <template v-slot:activator="{ props: activatorProps }">
                    <v-btn v-bind="activatorProps"
                        size="large"
                        color="grey"
                        icon="mdi-cog"
                    />
                </template>
                <v-dialog width="auto">
                    <template v-slot:activator="{ props: activatorProps }">
                        <v-btn key="1" icon="mdi-pencil" color="black" v-bind="activatorProps"/>
                    </template>
                    <template v-slot:default="{ isActive }">
                        <DialogProcess :api="api"
                            :edit="process"
                            :tools="tools"
                            @completed="$emit('reload', false)"
                            @close-dialog="isActive.value = false"
                        />
                    </template>
                </v-dialog>
                <v-dialog width="500" class="overflow-auto">
                    <template v-slot:activator="{ props: activatorProps }">
                        <v-btn key="2" icon="mdi-trash-can-outline" color="red" v-bind="activatorProps"/>
                    </template>
                    <template v-slot:default="{ isActive }">
                        <DialogDelete
                            :api="api"
                            :id="process.id"
                            :text="`Process '${process.name}' will be removed`"
                            @completed="$emit('reload', false)"
                            @close-dialog="isActive.value = false"
                        />
                    </template>
                </v-dialog>
            </v-speed-dial>
        </v-card-actions>
    </v-card>
</template>

<script setup lang="ts">
    defineProps({
        api: Object,
        process: Object,
        tools: Array,
        details: Boolean
    })
    defineEmits(['reload'])
    const user = userStore()
</script>