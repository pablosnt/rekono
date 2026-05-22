<template>
  <UPopover v-model:open="open" :ui="{ content: 'p-0.5' }">
    <UTooltip text="Link">
      <UButton
        icon="i-lucide-link"
        color="neutral"
        active-color="primary"
        variant="ghost"
        active-variant="soft"
        size="sm"
        :active="active"
        :disabled="disabled"
        aria-label="Add or edit link"
      />
    </UTooltip>
    <template #content>
      <UInput
        v-model="url"
        autofocus
        name="url"
        type="url"
        inputmode="url"
        variant="none"
        placeholder="Paste a link..."
        @keydown="
          (event: KeyboardEvent) => {
            if (event.key === 'Enter') {
              event.preventDefault();
              setLink();
            }
          }
        "
      >
        <div class="flex items-center mr-0.5">
          <UButton
            icon="i-lucide-corner-down-left"
            variant="ghost"
            size="sm"
            :disabled="!url && !active"
            aria-label="Apply link"
            @click="setLink"
          />
          <USeparator orientation="vertical" class="h-6 mx-1" />
          <UButton
            icon="i-lucide-external-link"
            color="neutral"
            variant="ghost"
            size="sm"
            :disabled="!url && !active"
            aria-label="Open link in new window"
            @click="openLink"
          />
          <UButton
            icon="i-lucide-trash"
            color="neutral"
            variant="ghost"
            size="sm"
            :disabled="!url && !active"
            aria-label="Remove link"
            @click="
              () => {
                editor
                  .chain()
                  .focus()
                  .extendMarkRange('link')
                  .unsetLink()
                  .setMeta('preventAutolink', true)
                  .run();
                url = '';
                open = false;
              }
            "
          />
        </div>
      </UInput>
    </template>
  </UPopover>
</template>

<script setup lang="ts">
import type { Editor } from "@tiptap/vue-3";

const props = defineProps<{
  editor: Editor;
  autoOpen?: boolean;
}>();
const open = ref(false);
const url = ref("");
const active = computed(() => props.editor.isActive("link"));
const disabled = computed(() => {
  if (!props.editor.isEditable) return true;
  return props.editor.state.selection.empty && !props.editor.isActive("link");
});

watch(
  () => props.editor,
  (editor, _, onCleanup) => {
    if (!editor) return;
    const updateUrl = () => {
      const { href } = editor.getAttributes("link");
      url.value = href || "";
    };
    updateUrl();
    editor.on("selectionUpdate", updateUrl);
    onCleanup(() => {
      editor.off("selectionUpdate", updateUrl);
    });
  },
  { immediate: true },
);

watch(active, (isActive) => {
  if (isActive && props.autoOpen) {
    open.value = true;
  }
});

function setLink() {
  if (!url.value) return;
  const hasCode = props.editor.isActive("code");
  let chain = props.editor.chain().focus();
  if (hasCode && !props.editor.state.selection.empty) {
    chain = chain.extendMarkRange("code").setLink({ href: url.value });
  } else {
    chain = chain.extendMarkRange("link").setLink({ href: url.value });
    if (props.editor.state.selection.empty) {
      chain = chain.insertContent({ type: "text", text: url.value });
    }
  }
  chain.run();
  open.value = false;
}

function openLink() {
  if (!url.value) return;
  window.open(url.value, "_blank", "noopener,noreferrer");
}
</script>
