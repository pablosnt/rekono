<template>
  <center class="mt-5">
    <h1><strong>NOT FOUND</strong></h1>
    <br>
    <p>The page that you are looking for is not here.</p>
    <br>
    <b-button variant="danger" @click="comeBack">Go back!</b-button>
  </center>
</template>

<script>
export default {
  name: 'pageNotFound',
  props: {
    back: {
      type: String,
      default: '/'
    }
  },
  methods: {
    comeBack () {
      this.$router.push(this.back)
    }
  }
}
</script>

