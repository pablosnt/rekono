<script setup lang="ts">
useHead({
  meta: [{ name: "viewport", content: "width=device-width, initial-scale=1" }],
  link: [{ rel: "icon", href: "/favicon-light.png", type: "image/png" }],
  htmlAttrs: {
    lang: "en",
  },
});

const title = "Rekono";
const description =
  "Offensive security platform that automates attack surface discovery and vulnerability management";

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  ogImage:
    "https://raw.githubusercontent.com/pablosnt/rekono/refs/heads/main/frontend/public/logo-light.png",
  twitterImage:
    "https://raw.githubusercontent.com/pablosnt/rekono/refs/heads/main/frontend/public/logo-light.png",
  twitterCard: "summary_large_image",
});
</script>

<template>
  <UApp :toaster="{ position: 'bottom-right', expand: false }">
    <NuxtLayout
      name="default"
      :class="{ '!min-h-0': !isPublicRoute($route.name) }"
    >
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
