<template>
  <div
    v-if="isPublicRoute($route.name) || isNeutralRoute($route.name)"
    class="h-screen overflow-hidden"
  >
    <UMain class="flex flex-col items-center justify-center gap-4 p-4">
      <UPageCard class="w-full max-w-md" variant="ghost">
        <UMain>
          <slot />
        </UMain>
      </UPageCard>
    </UMain>
  </div>
  <PanelProject v-else-if="$route.params.project_id">
    <slot />
  </PanelProject>
  <PanelMain v-else>
    <slot />
  </PanelMain>
</template>
