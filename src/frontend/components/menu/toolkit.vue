<template>
  <BaseMenu
    :options="[
      { title: 'Tools', icon: 'mdi-rocket', to: '/toolkit/tools' },
      {
        title: 'Processes',
        icon: 'mdi-robot-angry',
        to: '/toolkit/processes',
      },
      {
        title: 'Wordlists',
        icon: 'mdi-file-word-box',
        to: '/toolkit/wordlists',
      },
    ]"
  >
    <slot />
  </BaseMenu>
</template>
