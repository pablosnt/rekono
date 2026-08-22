<template>
  <PublicPage v-if="isPublicRoute($route.name) || isNeutralRoute($route.name)">
    <slot />
  </PublicPage>
  <PanelProject v-else-if="$route.params.project_id">
    <slot />
  </PanelProject>
  <PanelMain v-else>
    <slot />
  </PanelMain>
</template>
