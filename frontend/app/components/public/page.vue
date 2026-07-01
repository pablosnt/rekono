<template>
  <div class="h-screen overflow-hidden">
    <UMain class="flex flex-col items-center justify-center gap-4 p-4">
      <UPageCard class="w-full max-w-md" variant="ghost">
        <UMain>
          <slot />
        </UMain>
      </UPageCard>
    </UMain>
  </div>
</template>
