<template>
  <UPageSection
    title="Join the Community"
    :features="[
      {
        title: 'GitHub',
        description: 'Star us',
        icon: 'i-simple-icons-github',
        to: 'https://github.com/pablosnt/rekono',
        target: '_blank',
        orientation: 'vertical',
        ui: { root: 'text-center', leadingIcon: 'text-neutral' },
      },
      {
        title: 'Twitter',
        description: 'Follow us',
        icon: 'i-simple-icons-x',
        to: 'https://x.com/rekonosec',
        target: '_blank',
        orientation: 'vertical',
        ui: { root: 'text-center', leadingIcon: 'text-neutral' },
      },
      {
        title: 'Discord',
        description: 'Join us',
        icon: 'i-simple-icons-discord',
        to: 'https://discord.gg/Zyduu5C7M3',
        target: '_blank',
        orientation: 'vertical',
        ui: { root: 'text-center', leadingIcon: 'text-indigo-500' },
      },
      {
        title: 'Ko-fi',
        description: 'Support us',
        icon: 'i-simple-icons-kofi',
        to: 'https://ko-fi.com/pablosnt',
        target: '_blank',
        orientation: 'vertical',
        ui: { root: 'text-center', leadingIcon: 'text-primary' },
      },
      {
        title: 'Buy Me a Coffee',
        description: 'Support us',
        icon: 'i-simple-icons-buymeacoffee',
        to: 'https://buymeacoffee.com/pablosnt',
        target: '_blank',
        orientation: 'vertical',
        ui: { root: 'text-center', leadingIcon: 'text-warning' },
      },
      {
        title: 'Docs',
        description: 'Read us',
        icon: 'i-simple-icons-readthedocs',
        to: 'https://github.com/pablosnt/rekono/wiki',
        target: '_blank',
        orientation: 'vertical',
        ui: { root: 'text-center', leadingIcon: 'text-neutral' },
      },
    ]"
  />
</template>
