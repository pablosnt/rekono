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
          <v-text-field
            v-model="newTag"
            class="mt-2"
            :label="tags.length === 0 ? 'Tags' : null"
            prepend-inner-icon="mdi-tag"
            variant="outlined"
            :rules="[
              (t) => !t || validate.name.test(t.trim()) || 'Invalid tag',
            ]"
            validate-on="input"
            density="compact"
          >
            <template #append-inner>
              <v-btn
                icon="mdi-plus-thick"
                color="green"
                variant="text"
                :disabled="
                  !newTag ||
                  !newTag.trim() ||
                  !validate.name.test(newTag.trim()) ||
                  tags.includes(newTag.trim())
                "
                @click="
                  tags.push(newTag.trim());
                  newTag = null;
                "
              />
            </template>
            <v-chip-group class="justify-center" multiple>
              <v-chip
                v-for="tag in tags"
                :key="tag"
                :text="tag"
                closable
                @click:close="tags.splice(tags.indexOf(tag), 1)"
              />
            </v-chip-group>
          </v-text-field>
        </v-col>
        <v-col cols="2">
          <!-- TODO: Replace by button & icon. Floating button? -->
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
        <div v-if="preview" v-html="mdBody" />
      </v-row>
      <!-- TODO: Create / Save floating button -->
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import MarkdownIt from "markdown-it";

const validate = useValidation();
// TODO: Review & apply all plugins
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

const project = ref(null);
const target = ref(null);
const tags = ref([]);
const newTag = ref(null);
const body = ref(null);
const mdBody = ref(null);
const preview = ref(false);

const projects = ref([]);
const targets = ref([]);

// TODO: always allow manual creation/edition. Automatically create the note some minutes after first body edition/createFunctionExpression. If automatic save is already enabled, update the note also on the dialog close
</script>
