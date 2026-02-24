<template>
  <UFooter>
    <template #left>
      <UNavigationMenu
        :items="[
          {
            icon: 'i-simple-icons-github',
            to: 'https://github.com/pablosnt/rekono',
            target: '_blank',
          },
          {
            icon: 'i-simple-icons-kalilinux',
            to: 'https://www.kali.org/tools/rekono-kbx/',
            target: '_blank',
          },
          {
            icon: 'codicon:terminal-bash',
            to: 'https://github.com/pablosnt/rekono-cli',
            target: '_blank',
          },
          {
            icon: 'i-simple-icons-swagger',
            to: '/api/schema/swagger-ui.html',
            target: '_blank',
          },
          {
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
        <UAvatar
          src="/favicon.png"
          alt="Rekono"
          size="xs"
          :ui="{ root: 'bg-transparent' }"
          class="mr-2"
        />
        <p class="text-sm text-muted text-center">
          Rekono Maintainers © {{ new Date().getFullYear() }}
        </p>
      </div>
    </template>

    <template #right>
      <UNavigationMenu
        :items="[
          {
            icon: 'i-simple-icons-x',
            to: 'https://x.com/rekonosec',
            target: '_blank',
          },
          {
            icon: 'i-simple-icons-discord',
            to: 'https://discord.gg/Zyduu5C7M3',
            target: '_blank',
          },
          {
            icon: 'i-simple-icons-gmail',
            to: 'mailto:rekono.project@gmail.com',
            target: '_blank',
          },
          {
            icon: 'i-simple-icons-kofi',
            to: 'https://ko-fi.com/pablosnt',
            target: '_blank',
          },
          {
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
