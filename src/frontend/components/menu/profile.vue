<template>
  <Menu
    :options="[
      {
        title: 'Personal Information',
        icon: 'mdi-account',
        to: '/profile',
      },
      {
        title: 'Security',
        icon: 'mdi-lock',
        to: '/profile/security',
      },
      {
        title: 'Telegram Bot',
        icon: 'mdi-robot',
        to: '/profile/telegram-bot',
      },
      {
        title: 'HTTP Headers',
        icon: 'mdi-web',
        to: '/profile/http-headers',
      },
    ]"
  >
    <slot />
  </Menu>
</template>
