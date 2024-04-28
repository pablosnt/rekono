<template>
    <Menu         
        :options="[{ title: 'Tools', icon: 'mdi-rocket', to: '/resources/tools' }, { title: 'Processes', icon: 'mdi-robot', to: '/resources/processes' }, { title: 'Wordlists', icon: 'mdi-file-word-box', to: '/resources/wordlists' }]"
    >
        <slot/>
    </Menu>
</template>