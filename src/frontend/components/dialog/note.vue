<template>
  <v-card
    class="mx-auto"
    elevation="3"
    :subtitle="
      currentNote ? new Date(currentNote.updated_at).toUTCString() : undefined
    "
    :loading="loading ? 'red' : false"
  >
    <template #title>
      <v-text-field
        v-model="title"
        class="note-title font-weight-black"
        placeholder="Title"
        variant="text"
        density="comfortable"
        focused
        validate-on="input"
        :rules="[(t) => !t || validate.name.test(t) || 'Invalid title value']"
        @update:model-value="disabled = false"
      />
    </template>
    <template #append>
      <v-container>
        <v-spacer />
        <v-row v-if="currentNote" dense>
          <ButtonNoteLink
            :target="target"
            :task="task"
            :execution="execution"
            :osint="osint"
            :host="host"
            :port="port"
            :path="path"
            :credential="credential"
            :technology="technology"
            :vulnerability="vulnerability"
            :exploit="exploit"
            :note="note"
          />
          <span class="me-2" />
          <MiscNoteForkedFrom v-if="note" :note="note" />
          <span class="me-2" />
          <MiscNoteForks :note="currentNote" />
          <span class="me-2" />
          <ButtonLike
            :api="api"
            :item="currentNote"
            @reload="
              (value) =>
                api
                  .get(currentNote.id)
                  .then((response) => (currentNote = response))
            "
          />
          <span class="me-4" />
          <MiscOwner :entity="currentNote" />
          <span class="me-2" />
          <ButtonDelete
            v-if="currentNote"
            :id="currentNote.id"
            :api="api"
            :text="`Note '${currentNote.title}' will be removed`"
            icon="mdi-trash-can"
            @completed="
              note
                ? navigateTo(`/projects/${note.project}/notes`)
                : $emit('completed')
            "
          />
          <span class="me-2" />
          <v-btn
            v-if="!note"
            icon="mdi-close"
            variant="text"
            @click="
              autoSave ? submit(true) : null;
              $emit('closeDialog');
            "
          />
        </v-row>
        <v-row dense>
          <v-spacer />
          <ButtonNoteLink
            v-if="!currentNote"
            :target="target"
            :task="task"
            :execution="execution"
            :osint="osint"
            :host="host"
            :port="port"
            :path="path"
            :credential="credential"
            :technology="technology"
            :vulnerability="vulnerability"
            :exploit="exploit"
            :note="note"
          />
          <span class="me-2" />
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
            v-model="preview"
            icon
            variant="text"
            @click="preview = !preview"
          >
            <v-icon :icon="preview ? 'mdi-pencil' : 'mdi-eye'" />
            <v-tooltip
              activator="parent"
              :text="preview ? 'Edit' : 'Preview'"
            />
          </v-btn>
          <v-btn
            v-model="autoSave"
            icon
            variant="text"
            @click="autoSave = !autoSave"
          >
            <v-icon icon="mdi-floppy" :color="autoSave ? 'green' : 'red'" />
            <v-tooltip
              activator="parent"
              :text="
                autoSave
                  ? 'Auto-Save: On. Note will be saved each minute'
                  : 'Auto-Save: Off'
              "
            />
          </v-btn>

          <span class="me-2" />
          <v-btn
            v-if="!note && !currentNote"
            icon="mdi-close"
            variant="text"
            @click="
              autoSave ? submit(true) : null;
              $emit('closeDialog');
            "
          />
        </v-row>
      </v-container>
    </template>
    <template #text>
      <InputTag
        class="mt-2"
        :value="tags"
        @new-values="
          (value) => {
            disabled = false;
            tags = value;
          }
        "
      />
      <v-textarea
        v-if="!preview"
        v-model="body"
        variant="solo"
        placeholder="Markdown content"
        rows="40"
        width="100%"
        heigh="100%"
        counter
        @update:model-value="
          disabled = false;
          markdownBody = body ? markdown.render(body) : null;
        "
      />
      <v-container v-if="preview" fluid>
        <!-- eslint-disable-next-line vue/no-v-html  -->
        <div v-if="markdownBody" class="note-body-md" v-html="markdownBody" />
      </v-container>
    </template>
    <v-fab
      color="red"
      icon
      class="position-fixed"
      location="bottom"
      size="64"
      :disabled="disabled"
      app
      @click="submit(true)"
    >
      <v-icon icon="mdi-floppy" />
      <v-tooltip activator="parent" text="Save" />
    </v-fab>
  </v-card>
</template>

<script setup lang="ts">
const props = defineProps({
  api: {
    type: Object,
    required: false,
    default: useApi("/api/notes/", true, "Note"),
  },
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
});
const emit = defineEmits(["completed", "closeDialog"]);
const validate = useValidation();
const markdown = useMarkdown()

const title = ref(null);
const shared = ref(false);
const tags = ref([]);
const body = ref(null);

if (props.note) {
  title.value = props.note.title;
  shared.value = props.note.public;
  tags.value = props.note.tags;
  body.value = props.note.body;
}

const loading = ref(false);
const disabled = ref(true);
const autoSave = ref(true);
const autoSaveSeconds = 60;
const preview = ref(body.value);
const currentNote = ref(props.note);
const markdownBody = ref(
  preview.value ? markdown.render(body.value) : null,
);
autoSubmit();

function autoSubmit() {
  setTimeout(() => {
    if (autoSave.value) {
      submit(false);
    }
    autoSubmit();
  }, autoSaveSeconds * 1000);
}

function success(completed, response) {
  currentNote.value = response;
  disabled.value = true;
  loading.value = false;
  if (completed) {
    if (props.note) {
      return navigateTo(`/projects/${response.project}/notes`);
    } else {
      emit("completed");
      emit("closeDialog");
    }
  }
}

function submit(completed) {
  if ((!title.value || validate.name.test(title.value)) && !disabled.value) {
    let data = {
      title: title.value ? title.value : "Untitled",
      body: body.value,
      tags: tags.value,
      public: shared.value,
    };
    if (currentNote.value) {
      data = Object.assign({}, data, {
        project: currentNote.value.project,
        target: currentNote.value.target,
        task: currentNote.value.task,
        execution: currentNote.value.execution,
        osint: currentNote.value.osint,
        host: currentNote.value.host,
        port: currentNote.value.port,
        path: currentNote.value.path,
        credential: currentNote.value.credential,
        technology: currentNote.value.technology,
        vulnerability: currentNote.value.vulnerability,
        exploit: currentNote.value.exploit,
      });
      loading.value = true;
      props.api
        .update(data, currentNote.value.id)
        .then((response) => success(completed, response))
        .catch(() => (loading.value = false));
    } else {
      data = Object.assign({}, data, {
        project: props.parameters ? props.parameters.project : props.project,
        target: props.target ? props.target.id : null,
        task: props.task ? props.task.id : null,
        execution: props.execution ? props.execution.id : null,
        osint: props.osint ? props.osint.id : null,
        host: props.host ? props.host.id : null,
        port: props.port ? props.port.id : null,
        path: props.path ? props.path.id : null,
        credential: props.credential ? props.credential.id : null,
        technology: props.technology ? props.technology.id : null,
        vulnerability: props.vulnerability ? props.vulnerability.id : null,
        exploit: props.exploit ? props.exploit.id : null,
      });
      loading.value = true;
      props.api
        .create(data)
        .then((response) => success(completed, response))
        .catch(() => (loading.value = false));
    }
  }
}
</script>

<style lang="css">
.note-title .v-input__control .v-field .v-field__field .v-field__input {
  font-size: 2.75em;
  line-height: 2;
}
.note-body-md table,
.note-body-md th,
.note-body-md td {
  border: 1px solid black;
  border-collapse: collapse;
  padding: 5px;
}
.note-body-md th {
  background-color: rgb(200, 69, 69);
}
.note-body-md blockquote {
  padding: 10px 20px;
  margin: 0 0 20px;
  font-size: 17.5px;
  border-left: 5px solid #eee;
}
.note-body-md p code,
.note-body-md li code,
.note-body-md blockquote code,
.note-body-md td code {
  padding: 2px 4px;
  font-size: 90%;
  color: #c7254e;
  background-color: #f9f2f4;
  border-radius: 4px;
}
</style>
