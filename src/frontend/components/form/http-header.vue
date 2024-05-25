<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-container fluid>
      <v-row justify="center" dense>
        <v-col cols="4">
          <v-text-field
            v-model="key"
            class="text-medium-emphasis"
            variant="outlined"
            label="Header"
            hide-details
            clearable
            @update:model-value="disabled = false"
          />
        </v-col>
        <v-col cols="8">
          <v-text-field
            v-model="value"
            variant="outlined"
            label="Value"
            hide-details
            clearable
            @update:model-value="disabled = false"
          >
            <template #prepend>:</template>
            <template v-if="header !== null" #append>
              <v-btn
                :disabled="disabled"
                variant="text"
                icon="mdi-tray-arrow-down"
                color="green"
                @click="submit()"
              />
              <v-dialog width="500" class="overflow-auto">
                <template #activator="{ props: activatorProps }">
                  <v-btn hover variant="text" icon v-bind="activatorProps">
                    <v-icon icon="mdi-close" color="red" />
                    <v-tooltip activator="parent" text="Delete" />
                  </v-btn>
                </template>
                <template #default="{ isActive }">
                  <DialogDelete
                    :id="header.id"
                    :api="api"
                    :text="`HTTP header '${header.key}' will be removed`"
                    @completed="
                      $emit('completed');
                      isActive.value = false;
                    "
                    @close-dialog="isActive.value = false"
                  />
                </template>
              </v-dialog>
            </template>
          </v-text-field>
        </v-col>
      </v-row>
      <v-btn
        v-if="!header"
        color="red"
        size="large"
        variant="tonal"
        text="Save"
        type="submit"
        class="mt-5"
        block
        autofocus
        :disabled="disabled"
      />
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  header: {
    type: Object,
    required: false,
    default: null,
  },
});
const emit = defineEmits(["completed", "loading"]);

const valid = ref(true);
const disabled = ref(props.header !== null);
const key = ref(props.header ? props.header.key : null);
const value = ref(props.header ? props.header.value : null);

function submit() {
  if (valid.value) {
    let request = null;
    const body = { key: key.value.trim(), value: value.value.trim() };
    if (props.header) {
      request = props.api.update(body, props.header.id);
    } else {
      request = props.api.create(body);
    }
    emit("loading", true);
    request
      .then(() => {
        emit("loading", false);
        emit("completed");
      })
      .catch(() => emit("loading", false));
  }
}
</script>
