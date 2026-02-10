<template>
  <ProjectPanel v-if="$route.params.project_id">
    <slot />
  </ProjectPanel>
  <MainPanel v-else>
    <slot />
  </MainPanel>
</template>
