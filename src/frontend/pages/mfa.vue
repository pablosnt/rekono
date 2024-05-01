<template>
    <NuxtLayout name="public-form">
        <v-card-title class="text-center">Multi Factor Authentication</v-card-title>

        <v-card-text v-if="app" class="text-center">Type your OTP from your authentication app</v-card-text>
        <v-card-text v-if="!app" class="text-center">Type the OTP sent to your email</v-card-text>
        
        <v-form @submit.prevent="loading = true; login(mfa)">
            <v-otp-input v-if="app"
                v-model="mfa"
                variant="solo"
                autofocus
                validate-on="blur"
                :rules="[o => !!o || 'OTP is required']"
            />
            
            <v-text-field v-if="!app"
                v-model="mfa"
                density="compact"
                label="OTP"
                prepend-inner-icon="mdi-account-key"
                variant="outlined"
                autofocus
                validate-on="blur"
                :rules="[o => !!o || 'OTP is required', o => o.length === 128 || 'Invalid OTP']"
            />

            <v-card-actions class="justify-center">
                <v-btn v-if="!loading"
                    class="mb-8"
                    color="red"
                    size="large"
                    variant="tonal"
                    text="Login"
                    type="submit"
                    block
                />
                <v-progress-circular v-if="loading" color="error" indeterminate/>
            </v-card-actions>

            <div class="text-center">
                <v-btn @click.prevent="app=!app; mfa = null; !app ? emailApi.create({ token: token }) : null">Use {{ app ? 'email' : 'app' }} instead</v-btn>
            </div>
        </v-form>
    </NuxtLayout>
</template>


<script setup lang="ts">
    definePageMeta({layout: false})
    const app = ref(true)
    const mfa = ref(null)
    const loading = ref(false)
    const router = useRouter()
    const tokens = useTokens()
    const token = ref(tokens.get().mfa)
    const api = useApi('/api/security/mfa/', false, false)
    const emailApi = ref(useApi('/api/security/mfa/email/', false, false))
    function login(value: string) {
        api.create({ token: token.value, mfa: value })
            .then((response) => {
                const isLogin = tokens.save(response)
                loading.value = false
                if (isLogin) {
                    router.push({ name: 'index' })
                }
            })
            .catch(() => { loading.value = false })
    }
</script>