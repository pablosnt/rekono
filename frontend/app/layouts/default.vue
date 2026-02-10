<template>
  <PanelProject v-if="$route.params.project_id">
    <slot />
  </PanelProject>
  <PanelMain v-else>
    <slot />
  </PanelMain>
</template>
