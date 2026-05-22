<template>
  <NodeViewWrapper>
    <UFileUpload
      v-model="file"
      accept="image/jpeg,image/png,image/webp,image/gif"
      label="Upload an image"
      :description="`PNG, JPG, WEBP or GIF (max. ${MAX_MB_SIZE}MB)`"
      :preview="false"
      class="min-h-48"
    >
      <template #leading>
        <UAvatar
          :icon="loading ? 'i-lucide-loader-circle' : 'i-lucide-image'"
          size="xl"
          :ui="{ icon: [loading && 'animate-spin'] }"
        />
      </template>
    </UFileUpload>
  </NodeViewWrapper>
</template>

<script setup lang="ts">
import type { NodeViewProps } from "@tiptap/vue-3";
import { NodeViewWrapper } from "@tiptap/vue-3";

const props = defineProps<NodeViewProps>();
const file = ref<File | null>(null);
const loading = ref(false);
const toast = useToast();
const MAX_MB_SIZE = ref(2);
const MAX_SIZE = MAX_MB_SIZE.value * 1024 * 1024;

watch(file, (newFile) => {
  if (!newFile) return;
  if (newFile.size > MAX_SIZE) {
    toast.add({
      title: "File too large",
      description: "Maximum file size is 2MB",
      color: "error",
    });
    file.value = null;
    return;
  }
  loading.value = true;
  const reader = new FileReader();
  reader.addEventListener("load", async (e) => {
    const dataUrl = e.target?.result as string;
    if (!dataUrl) {
      loading.value = false;
      return;
    }
    await new Promise((resolve) => {
      setTimeout(resolve, 1000);
    });
    const pos = props.getPos();
    if (typeof pos !== "number") {
      loading.value = false;
      return;
    }
    props.editor
      .chain()
      .focus()
      .deleteRange({ from: pos, to: pos + 1 })
      .setImage({ src: dataUrl })
      .run();

    loading.value = false;
  });
  reader.readAsDataURL(newFile);
});
</script>
