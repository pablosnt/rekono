<template>
  <Menu
    :options="[
      {
        title: 'Settings',
        icon: 'mdi-cog',
        to: '/administration/settings',
      },
      {
        title: 'Notifications',
        icon: 'mdi-bell-ring',
        to: '/administration/notifications',
      },
      {
        title: 'Integrations',
        icon: 'mdi-connection',
        to: '/administration/integrations',
      },
      {
        title: 'HTTP Headers',
        icon: 'mdi-web',
        to: '/administration/http-headers',
      },
      {
        title: 'Targets Denylist',
        icon: 'mdi-wall',
        to: '/administration/target-denylist',
      },
      {
        title: 'Users',
        icon: 'mdi-account-group',
        to: '/administration/users',
      },
    ]"
  >
    <slot />
  </Menu>
</template>
