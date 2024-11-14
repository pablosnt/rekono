<template>
  <v-footer
    class="mt-10 bg-red-darken-3 ma-0 pa-0"
    :app="app"
    style="z-index: auto"
  >
    <v-container max-height="400">
      <v-row justify="space-around" align="center">
        <v-col
          v-for="section in Object.keys(footer)"
          :key="section"
          class="text-center"
        >
          <p class="text-overline">{{ section }}</p>
          <template v-for="item in footer[section]" :key="item.link">
            <BaseButton
              v-if="item.icon"
              class="mx-3"
              :href="item.link"
              icon
              variant="plain"
              new-tab
            >
              <template #icon>
                <v-icon
                  v-if="item.icon.substring(0, 4) === 'mdi-'"
                  size="large"
                  :icon="item.icon"
                />
                <Icon
                  v-if="item.icon.substring(0, 4) !== 'mdi-'"
                  :icon="item.icon"
                  height="28"
                  width="28"
                />
              </template>
            </BaseButton>
          </template>
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-label
          >© {{ new Date().getFullYear() }} Rekono Mantainers. All rights
          reserved</v-label
        >
      </v-row>
    </v-container>
  </v-footer>
  <div
    v-intersect="(isIntersecting, entries, observer) => (app = isIntersecting)"
  />
</template>

<script setup lang="ts">
import { Icon } from "@iconify/vue";
const app = ref(true);
const footer = ref({
  Project: [
    {
      icon: "mdi-github",
      color: "black",
      link: "https://github.com/pablosnt/rekono",
    },
    // todo: Update link to the new GitHub pages when ready
    {
      icon: "mdi-file-document",
      link: "https://github.com/pablosnt/rekono/wiki",
    },
    {
      icon: "mdi-api",
      link: "/api/schema/swagger-ui.html",
    },
    {
      icon: "mdi-console",
      link: "https://github.com/pablosnt/rekono-cli",
    },
    {
      icon: "simple-icons:kalilinux",
      link: "https://www.kali.org/tools/rekono-kbx/",
    },
  ],
  "Contact Us": [
    {
      icon: "line-md:twitter-x",
      link: "https://x.com/rekonosec",
    },
    {
      icon: "ic:baseline-discord",
      link: "https://discord.gg/Zyduu5C7M3",
    },
    {
      icon: "mdi-gmail",
      link: "mailto:rekono.project@gmail.com",
    },
  ],
  "Support Us": [
    {
      icon: "simple-icons:kofi",
      link: "https://ko-fi.com/pablosnt",
    },
    {
      icon: "line-md:buy-me-a-coffee-filled",
      link: "https://buymeacoffee.com/pablosnt",
    },
  ],
});
</script>
