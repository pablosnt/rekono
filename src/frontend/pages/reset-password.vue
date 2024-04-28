<template>
    <NuxtLayout name="public-form">
        <v-card-text class="text-center">You will receive via email a link to reset your password</v-card-text>
        <v-form @submit.prevent="resetPassword(otp ? { otp: otp._value, password: password } : { email: email })">
            <v-text-field v-if="!otp"
                v-model="email"
                density="compact"
                label="Email"
                prepend-inner-icon="mdi-email"
                variant="outlined"
                :rules="[e => !!e || 'Email is required', e => /^[\w.-]+@[\w-]+\.[\w.-]+$/.test(e) || 'Invalid Email address']"
                validate-on="blur"
            />

            <v-text-field v-if="otp"
                v-model="password"
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

            <v-text-field v-if="otp"
                v-model="passwordConfirmation"
                :append-inner-icon="visibleConfirmation ? 'mdi-eye-off' : 'mdi-eye'"
                :type="visibleConfirmation ? 'text' : 'password'"
                density="compact"
                label="Confirm password"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                @click:append-inner="visibleConfirmation = !visibleConfirmation"
                :rules="[
                    p => !!p || 'Password confirmation is required',
                    p => p === password || 'Paswords do not match'
                ]"
                validate-on="blur"
            />

            <v-card-actions class="justify-center">
                <v-btn class="mb-8"
                    color="red"
                    size="large"
                    variant="tonal"
                    text="Reset Password"
                    type="submit"
                    block
                />
            </v-card-actions>
        </v-form>
    </NuxtLayout>
</template>

<script setup lang="ts">
    const visible = ref(false)
    const visibleConfirmation = ref(false)
    const email = ref(null)
    const password = ref(null)
    const passwordConfirmation = ref(null)
    const alert = useAlert()
    const route = useRoute()
    const router = useRouter()
    const otp = ref(route.query.otp ? route.query.otp : null)
    const { get, list, create, update, remove } = useApi('/api/users/reset-password/', false, false)
    function resetPassword(body: object) {
        if (body.otp) {
            update(body)
                .then(() => { router.push({ name: 'login' })})
        } else {
            create(body)
                .then(() => { alert('Done! You will receive via email a temporal link to change your password', 'success') })
        }
    }
</script>