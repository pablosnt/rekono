<template>
  <h1>{{ project.name }}</h1>
</template>

<script>
export default {
  name: 'projectDetails',
  props: {
    project: {
      type: Object,
      default: null
    }
  }
}
</script>
