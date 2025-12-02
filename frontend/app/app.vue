<script setup>
useHead({
  meta: [{ name: "viewport", content: "width=device-width, initial-scale=1" }],
  link: [{ rel: "icon", href: "/favicon.ico" }],
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
  // TODO: Update:
  ogImage: "https://ui.nuxt.com/assets/templates/nuxt/starter-light.png",
  twitterImage: "https://ui.nuxt.com/assets/templates/nuxt/starter-light.png",
  twitterCard: "summary_large_image",
});
</script>

<template>
  <UApp :toaster="{ position: 'top-right', expand: false }">
    <NuxtLayout>
      <UMain>
        <NuxtPage />
      </UMain>
    </NuxtLayout>
    <Footer />
  </UApp>
</template>
