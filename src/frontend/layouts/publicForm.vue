<template>
    <div id="public-page">
        <v-card id="public-form"
            class="mx-auto pa-3"
            elevation="8"
            max-width="448"
            rounded="lg"
            style="margin-top: 120px;"
        >
            <v-img src="/static/logo-black.png"
                class="mx-auto ma-4"
            ></v-img>
            <slot />
        </v-card>
    </div>
</template>

<script setup lang="ts">
// TODO: should this be defined as layout?
// TODO forward user to main page if they are authenticated
</script>

<style>
#public-page {
    height: 100%;
    background-image: url('/static/background.jpg');
    background-size: cover;
    background-repeat: no-repeat;
}
#public-form {
    background: white;
}
</style>