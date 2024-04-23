<template>
    <NuxtLayout name="public-form">
        <v-form @submit.prevent="login">
            <v-text-field v-model="username"
                density="compact"
                label="Username"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                :rules="[u => !!u || 'Username is required']"
                validate-on="blur"
            />

            <div class="text-subtitle-1 text-medium-emphasis d-flex align-center justify-space-between">
                <v-spacer/>
                <a class="text-caption text-decoration-none text-grey-darken-2"
                    href="/reset-password"
                >Reset password</a>
            </div>
            <v-text-field v-model="password"
                :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
                :type="visible ? 'text' : 'password'"
                density="compact"
                label="Password"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                @click:append-inner="visible = !visible"
                :rules="[p => !!p || 'Password is required']"
                validate-on="blur"
            />
            
            <v-card-actions class="justify-center">
                <v-btn class="mb-8"
                    color="red"
                    size="large"
                    variant="tonal"
                    text="Login"
                    type="submit"
                    block
                />
            </v-card-actions>
        </v-form>
    </NuxtLayout>
</template>

<script setup lang="ts">
    definePageMeta({layout: false})
    const visible = ref(false)
    const username = ref(null)
    const password = ref(null)
    const router = useRouter()
    const { getTokens, saveTokens, removeTokens } = useTokens()
    const { data, items, get, list, create, update, remove } = useApi('/api/security/login/', false, false)
    function login() {
        create({ username: username, password: password })
            .then((response) => {
                const isLogin = saveTokens(response)
                if (isLogin) {
                    router.push({ name: 'index' })
                } else {
                    router.push({ name: 'mfa' })
                }
            })
    }
</script>