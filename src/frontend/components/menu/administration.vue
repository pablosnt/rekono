<template>
  <Menu
    :options="[
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
        title: 'Monitoring',
        icon: 'mdi-radar',
        to: '/administration/monitoring',
      },
      {
        title: 'HTTP Headers',
        icon: 'mdi-web',
        to: '/administration/http-headers',
      },
      {
        title: 'Targets Denylist',
        icon: 'mdi-wall',
        to: '/administration/targets-denylist',
      },
      {
        title: 'Users',
        icon: 'mdi-account-group',
        to: '/administration/users',
      },
      {
        title: 'Settings',
        icon: 'mdi-cog',
        to: '/administration/settings',
      },
    ]"
  >
    <slot />
  </Menu>
</template>
