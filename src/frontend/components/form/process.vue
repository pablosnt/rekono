<template>
    <v-form v-model="valid" @submit.prevent="submit()">
        <v-text-field v-model="name"
            class="mt-2"
            label="Name"
            variant="outlined"
            :rules="[n => !!n || 'Name is required', n => validate.name.test(n) || 'Invalid name value']"
            validate-on="blur"
        />

        <v-textarea v-model="description"
            class="mt-2"
            label="Description"
            variant="outlined"
            :rules="[d => !!d || 'Description is required', d => validate.text.test(d) || 'Invalid description value']"
            validate-on="blur"
            auto-grow
            max-rows="10"
            rows="3"
        />

        <v-text-field v-model="newTag"
            class="mt-2"
            :label="tags.length === 0 ? 'Tags' : null"
            prepend-inner-icon="mdi-tag"
            variant="outlined"
            :rules="[t => validate.name.test(t.trim()) || 'Invalid tag']"
            validate-on="blur"
        >
            <template v-slot:append-inner >
                <v-btn icon="mdi-plus-thick"
                    color="green"
                    variant="text"
                    @click="tags.push(newTag.trim()); newTag = null"
                    :disabled="!newTag || !newTag.trim() || !validate.name.test(newTag.trim()) || tags.includes(newTag.trim())"
                />
            </template>
            <v-chip-group class="justify-center" multiple>
            <v-chip v-for="tag in tags"
                :key="tag"
                :text="tag"
                closable
                @click:close="tags.splice(tags.indexOf(tag), 1)"
            />
        </v-chip-group>
        </v-text-field>

        <v-btn color="red"
            size="large"
            variant="tonal"
            :text="!edit ? 'Create' : 'Update'"
            type="submit"
            class="mt-4"
            block
        />
    </v-form>
</template>

<script setup lang="ts">
    const props = defineProps({
        api: Object,
        edit: Object
    })
    const emit = defineEmits(['completed', 'loading'])
    const validate = ref(useValidation())
    const valid = ref(true)
    const name = ref(props.edit ? props.edit.name : null)
    const description = ref(props.edit ? props.edit.description : null)
    const tags = ref(props.edit ? props.edit.tags : [])
    const newTag = ref(null)
    function submit() {
        if (valid.value) {
            emit('loading', true)
            const request = props.edit ? props.api.update : props.api.create
            request({ name: name.value, description: description.value, tags: tags.value }, props.edit?.id)
                .then((data) => { emit('completed', data) })
                .catch(() => { emit('loading', false) })
        }
    }
</script>