<template>
    <v-container id="public-page" class="fill-height" fluid>
        <v-row justify="center">
            <v-col cols="4">
                <v-card id="public-form"
                    class="mx-auto pa-3"
                    elevation="8"
                    rounded="lg"
                >
                    <v-img class="mx-auto ma-4" src="/static/logo-black.png"/>
                    <slot />
                </v-card>
            </v-col>
            
        </v-row>
    </v-container>
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