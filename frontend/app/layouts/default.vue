<template>
  <div>
    <PanelProject v-show="$route.params.project_id">
      <slot />
    </PanelProject>
    <PanelMain v-show="!$route.params.project_id">
      <slot />
    </PanelMain>
  </div>
</template>
