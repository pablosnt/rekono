<template>
  <v-form>
    <v-container fluid>
      <v-row>
        <v-col cols="1">
          <v-btn
            v-model="shared"
            :color="shared ? 'red' : 'green'"
            stacked
            :prepend-icon="shared ? 'mdi-lock-open-variant' : 'mdi-lock'"
            variant="text"
            @click="shared = !shared"
            >{{ shared ? "Public" : "Private" }}</v-btn
          >
        </v-col>
        <v-col cols="11">
          <v-text-field
            v-model="title"
            class="text-h5"
            placeholder="Title"
            variant="solo"
          />
        </v-col>
      </v-row>
      <v-row justify="space-around">
        <v-col cols="8">
          <InputTag
            class="mt-2"
            :value="tags"
            @new-value="(value) => (tags = value)"
          />
        </v-col>
        <v-col cols="2">
          <!-- todo: Replace by button & icon. Floating button? -->
          <v-switch
            v-model="preview"
            color="red"
            :label="preview ? 'Preview' : 'Raw'"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-textarea
          v-if="!preview"
          v-model="body"
          variant="solo"
          placeholder="Markdown content"
          no-resize
          rows="38"
          width="100%"
          heigh="100%"
          counter
          @update:model-value="mdBody = markdown.render(body)"
        />
        <!-- eslint-disable-next-line vue/no-v-html  -->
        <div v-if="preview" v-html="mdBody" />
      </v-row>
      <!-- todo: Create / Save floating button -->
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import MarkdownIt from "markdown-it";

// const validate = useValidation();
// todo: Review & apply all plugins
const markdown = ref(
  MarkdownIt({
    html: false,
    xhtmlOut: false,
    breaks: true,
    linkify: true,
    typographer: true,
  }),
);

const title = ref(null);
const shared = ref(false);

// const project = ref(null);
// const target = ref(null);
const tags = ref([]);
const body = ref(null);
const mdBody = ref(null);
const preview = ref(false);

// const projects = ref([]);
// const targets = ref([]);

// todo: always allow manual creation/edition. Automatically create the note some minutes after first body edition/createFunctionExpression. If automatic save is already enabled, update the note also on the dialog close
</script>
