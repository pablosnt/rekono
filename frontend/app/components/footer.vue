<template>
  <UFooter
    :ui="{
      container:
        'py-2 lg:py-2 lg:flex lg:items-center lg:justify-between lg:gap-x-3',
    }"
  >
    <template #left>
      <UNavigationMenu
        aria-label="Project resources"
        :items="[
          {
            'aria-label': 'GitHub',
            icon: 'i-simple-icons-github',
            to: 'https://github.com/pablosnt/rekono',
            target: '_blank',
          },
          {
            'aria-label': 'Kali Linux',
            icon: 'i-simple-icons-kalilinux',
            to: 'https://www.kali.org/tools/rekono-kbx/',
            target: '_blank',
          },
          {
            'aria-label': 'Rekono CLI',
            icon: 'codicon:terminal-bash',
            to: 'https://github.com/pablosnt/rekono-cli',
            target: '_blank',
          },
          {
            'aria-label': 'API Documentation',
            icon: 'i-simple-icons-swagger',
            to: '/api/schema/swagger-ui.html',
            target: '_blank',
          },
          {
            'aria-label': 'Wiki',
            icon: 'i-simple-icons-readthedocs',
            to: 'https://github.com/pablosnt/rekono/wiki',
            target: '_blank',
          },
        ]"
        variant="link"
      />
    </template>

    <template #default>
      <div class="flex items-center justify-center w-full sm:w-auto">
        <UColorModeImage
          light="/favicon-light.ico"
          dark="/favicon-dark.ico"
          alt="Rekono logo"
          class="mr-2"
          width="20"
        />
        <p class="text-sm text-muted text-center">
          Rekono Maintainers © {{ new Date().getFullYear() }}
        </p>
      </div>
    </template>

    <template #right>
      <UNavigationMenu
        aria-label="Community"
        :items="[
          {
            'aria-label': 'X (formerly Twitter)',
            icon: 'i-simple-icons-x',
            to: 'https://x.com/rekonosec',
            target: '_blank',
          },
          {
            'aria-label': 'Discord community',
            icon: 'i-simple-icons-discord',
            to: 'https://discord.gg/Zyduu5C7M3',
            target: '_blank',
          },
          {
            'aria-label': 'Contact by email',
            icon: 'i-simple-icons-gmail',
            to: 'mailto:rekono.project@gmail.com',
            target: '_blank',
          },
          {
            'aria-label': 'Support on Ko-fi',
            icon: 'i-simple-icons-kofi',
            to: 'https://ko-fi.com/pablosnt',
            target: '_blank',
          },
          {
            'aria-label': 'Buy Me a Coffee',
            icon: 'i-simple-icons-buymeacoffee',
            to: 'https://buymeacoffee.com/pablosnt',
            target: '_blank',
          },
        ]"
        variant="link"
      />
    </template>
  </UFooter>
</template>
