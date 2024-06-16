<template>
  <v-layout>
    <v-app-bar color="black" density="compact">
      <nuxt-link to="/">
        <v-app-bar-title>
          <NuxtImg
            class="mt-2"
            src="/static/logo-white.png"
            alt="Rekono"
            width="130"
          />
        </v-app-bar-title>
      </nuxt-link>

      <v-spacer />

      <v-btn>
        <v-icon icon="mdi-menu" size="x-large" />
        <v-menu activator="parent" open-on-hover location="bottom">
          <v-list density="compact" nav>
            <v-list-item to="/profile" title="Profile">
              <template #prepend>
                <v-icon color="red" :icon="enums.roles[user.role].icon" />
              </template>
            </v-list-item>
            <v-list-item
              v-if="user.role !== 'Reader'"
              to="/resources"
              title="Resources"
            >
              <template #prepend>
                <v-icon color="red" icon="mdi-toolbox" />
              </template>
            </v-list-item>
            <v-list-item
              v-if="user.role === 'Admin'"
              to="/administration"
              title="Administration"
            >
              <template #prepend>
                <v-icon color="red" icon="mdi-cog" />
              </template>
            </v-list-item>
            <!-- todo: Update link to the new GitHub pages -->
            <v-list-item
              href="https://github.com/pablosnt/rekono/wiki"
              target="_blank"
              title="Documentation"
            >
              <template #prepend>
                <v-icon color="red" icon="mdi-file-document" />
              </template>
            </v-list-item>
            <v-list-item
              href="/api/schema/swagger-ui.html"
              target="_blank"
              title="API Rest"
            >
              <template #prepend>
                <v-icon color="red" icon="mdi-xml" />
              </template>
            </v-list-item>
            <!-- TODO: Forward to login doesn't work -->
            <v-list-item title="Logout" to="/login" @click="logout()">
              <template #prepend>
                <v-icon color="red" icon="mdi-logout-variant" />
              </template>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
    </v-app-bar>
    <slot />
  </v-layout>
</template>

<script setup lang="ts">
const enums = ref(useEnums());
const user = userStore();
const tokens = useTokens();
const router = useRouter();
const api = useApi("/api/security/logout/", true);
function logout() {
  console.log("HELLO");
  console.log(window.location);
  const refresh = tokens.get().refresh;
  if (refresh) {
    api.create({ refresh: refresh });
  }
  user.logout();
  tokens.remove();
}
</script>
