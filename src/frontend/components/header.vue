<template>
  <v-app-bar color="black" density="compact">
    <nuxt-link to="/" class="ml-4">
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
          <v-list-item v-if="autz.isAuditor()" to="/toolkit" title="Toolkit">
            <template #prepend>
              <v-icon color="red" icon="mdi-toolbox" />
            </template>
          </v-list-item>
          <v-list-item
            v-if="autz.isAdmin()"
            to="/administration"
            title="Administration"
          >
            <template #prepend>
              <v-icon color="red" icon="mdi-cog" />
            </template>
          </v-list-item>
          <v-list-item title="Logout" to="/login?logout=true">
            <template #prepend>
              <v-icon color="red" icon="mdi-logout-variant" />
            </template>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-btn>
  </v-app-bar>
</template>

<script setup lang="ts">
const enums = useEnums();
const autz = useAutz();
const user = userStore();
</script>
