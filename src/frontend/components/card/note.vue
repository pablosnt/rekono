<template>
  <v-card
    class="mx-auto"
    elevation="3"
    :subtitle="note ? new Date(note.updated_at).toUTCString() : undefined"
  >
    <template #title>
      <v-text-field
        v-model="title"
        class="note-title font-weight-black"
        placeholder="Title"
        variant="text"
        density="comfortable"
        focused
      />
    </template>
    <template #append>
      <!-- TODO: autosave button -->
      <!-- TODO: Add links to the resources (targets, tasks, findings) -->
      <v-btn v-model="preview" icon variant="text" @click="preview = !preview">
        <v-icon :icon="preview ? 'mdi-pencil' : 'mdi-eye'" />
        <v-tooltip activator="parent" :text="preview ? 'Edit' : 'Preview'" />
      </v-btn>
      <v-btn v-model="shared" icon variant="text" @click="shared = !shared">
        <v-icon
          :icon="shared ? 'mdi-lock-open-variant' : 'mdi-lock'"
          :color="shared ? 'red' : 'green'"
        />
        <v-tooltip
          activator="parent"
          :text="shared ? 'Public Note' : 'Private Note'"
        />
      </v-btn>

      <v-btn
        v-if="isCreation"
        icon="mdi-close"
        variant="text"
        @click="$emit('closeDialog')"
      />
    </template>
    <template #text>
      <InputTag
        class="mt-2"
        :value="tags"
        @new-values="(value) => (tags = value)"
      />
      <v-textarea
        v-if="!preview"
        v-model="body"
        variant="solo"
        placeholder="Markdown content"
        rows="35"
        width="100%"
        heigh="100%"
        counter
        @update:model-value="markdownBody = body ? markdown.render(body) : null"
      />
      <v-container v-if="preview" fluid>
        <!-- eslint-disable-next-line vue/no-v-html  -->
        <div v-if="markdownBody" v-html="markdownBody" />
      </v-container>
    </template>
  </v-card>
</template>

<script setup lang="ts">
import MarkdownIt from "markdown-it";
import hljs from "highlight.js";
const props = defineProps({
  api: Object,
  parameters: {
    type: Object,
    required: false,
    default: null,
  },
  project: {
    type: Number,
    required: false,
    default: null,
  },
  target: {
    type: Object,
    required: false,
    default: null,
  },
  task: {
    type: Object,
    required: false,
    default: null,
  },
  execution: {
    type: Object,
    required: false,
    default: null,
  },
  osint: {
    type: Object,
    required: false,
    default: null,
  },
  host: {
    type: Object,
    required: false,
    default: null,
  },
  port: {
    type: Object,
    required: false,
    default: null,
  },
  path: {
    type: Object,
    required: false,
    default: null,
  },
  credential: {
    type: Object,
    required: false,
    default: null,
  },
  technology: {
    type: Object,
    required: false,
    default: null,
  },
  vulnerability: {
    type: Object,
    required: false,
    default: null,
  },
  exploit: {
    type: Object,
    required: false,
    default: null,
  },
  note: {
    type: Object,
    required: false,
    default: null,
  },
  isCreation: {
    type: Boolean,
    required: false,
    default: true,
  },
});
defineEmits(["completed", "closeDialog"]);
const validate = useValidation();
// TODO: Review & apply all plugins
const markdown = ref(
  MarkdownIt({
    breaks: true,
    linkify: true,
    typographer: true,
    highlight: function (str, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(str, { language: lang, ignoreIllegals: true })
            .value;
        } catch (__) {}
      }
      return "";
    },
  }),
);

const projectId = ref(
  props.parameters ? props.parameters.project : props.project,
);
const title = ref(null);
const shared = ref(null);
const tags = ref([]);
const body = ref(null);

if (props.note) {
  title.value = props.note.title;
  shared.value = props.note.public;
  tags.value = props.note.tags;
  body.value = props.note.body;
}

const preview = ref(!props.isCreation && props.note && body.value);
const markdownBody = ref(preview.value ? markdown.value.render(body) : null);
</script>

<style lang="css">
.note-title .v-input__control .v-field .v-field__field .v-field__input {
  font-size: 3em;
  line-height: 1;
}
</style>
