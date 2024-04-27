<template>
    <div id="public-page">
        <v-card id="public-form"
            class="mx-auto pa-3"
            elevation="8"
            max-width="448"
            rounded="lg"
            style="margin-top: 120px;"
        >
            <v-img class="mx-auto ma-4"
                src="/static/logo-black.png"
            />
            <slot />
        </v-card>
    </div>
</template>

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