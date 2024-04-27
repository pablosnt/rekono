<template>
    <NuxtLayout name="public-form">
        <v-card-title class="text-center">Multi Factor Authentication</v-card-title>

        <v-card-text v-if="app" class="text-center">Type your OTP from your authentication app</v-card-text>
        <v-card-text v-if="!app" class="text-center">Type the OTP sent to your email</v-card-text>
        
        <v-form @submit.prevent="login(mfa)">
            <v-otp-input v-if="app"
                v-model="mfa"
                variant="solo"
                focused
                validate-on="blur"
                :rules="[o => !!o || 'OTP is required']"
            />
            
            <v-text-field v-if="!app"
                v-model="mfa"
                density="compact"
                label="OTP"
                prepend-inner-icon="mdi-account-key"
                variant="outlined"
                :rules="[o => !!o || 'OTP is required', o => o.length === 128 || 'Invalid OTP']"
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

            <div class="text-center">
                <v-btn @click.prevent="app=!app; changeMethod()">Use {{ app ? 'email' : 'app' }} instead</v-btn>
            </div>
        </v-form>
    </NuxtLayout>
</template>


<script setup lang="ts">
    definePageMeta({layout: false})
    const app = ref(true)
    const mfa = ref(null)
    const router = useRouter()
    const { getTokens, saveTokens, removeTokens } = useTokens()
    function changeMethod() {
        if (!app._value) {
            const { data, items, get, list, create, update, remove } = useApi('/api/security/mfa/email/', false, false)
            create({ token: getTokens().mfa })
        }
    }
    function login(value: string) {
        const { data, items, get, list, create, update, remove } = useApi('/api/security/mfa/', false, false)
        create({ token: getTokens().mfa, mfa: value })
            .then((response) => {
                const isLogin = saveTokens(response)
                if (isLogin) {
                    router.push({ name: 'index' })
                }
            })
    }
</script>