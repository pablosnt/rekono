<template>
    <v-layout>
        <v-app-bar color="black" density="compact">
            <v-app-bar-title>
                <NuxtImg class="mt-2"
                    src="/static/logo-white.png"
                    alt="Rekono"
                    width="130"
                />
            </v-app-bar-title>
            <v-tabs v-model="tab" selected-class="text-red">
                <v-tab value="home" to="/">Home</v-tab>
                <v-tab value="projects" to="/projects">Projects</v-tab>
                <v-tab value="reports" to="/reports">Reports</v-tab>
                <v-tab value="notes" to="/notes">Notes</v-tab>
                <v-tab value="resources" to="/resources">Resources</v-tab>
                <v-tab v-if="user.role === 'Admin'"
                    value="administration"
                    to="/administration"
                >Administration</v-tab>
            </v-tabs>

            <v-spacer/>

            <v-btn>
                <v-icon icon="mdi-dots-vertical" size="x-large"/>
                <v-menu activator="parent"
                    open-on-hover
                    location="bottom"
                >
                    <v-list density="compact" nav>
                        <v-list-item to="/profile" title="Profile">
                            <template v-slot:prepend>
                                <v-icon color="red" icon="mdi-account"/>
                            </template>
                        </v-list-item>
                        <v-list-item href="https://github.com/pablosnt/rekono/wiki"
                            target="_blank"
                            title="Documentation"
                        >
                            <template v-slot:prepend>
                                <v-icon color="red" icon="mdi-file-document"/>
                            </template>
                        </v-list-item>
                        <v-list-item href="/api/schema/swagger-ui.html"
                            target="_blank"
                            title="API Rest"
                        >
                            <template v-slot:prepend>
                                <v-icon color="red" icon="mdi-xml"/>
                            </template>
                        </v-list-item>
                        <v-list-item title="Logout" @click.prevent="logout">
                            <template v-slot:prepend>
                                <v-icon color="red" icon="mdi-logout-variant"/>
                            </template>
                        </v-list-item>
                    </v-list>
                </v-menu>
            </v-btn>
        </v-app-bar>
        <slot/>
    </v-layout>
</template>

<script setup lang="ts">
    const route = useRoute()
    const tab = computed(() => { return route.path === '/' ? 'home' : route.path.split('/')[1].toLowerCase()})
    const user = userStore()
    const router = useRouter()
    const { getTokens, saveTokens, removeTokens } = useTokens()
    const { data, items, get, list, create, update, remove } = useApi('/api/security/logout/', true, false)
    function logout() {
        create({ refresh: getTokens().refresh})
        user.logout()
        removeTokens()
        router.push({ name: 'login' })
    }
</script>