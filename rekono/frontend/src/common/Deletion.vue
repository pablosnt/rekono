<template>
  <b-modal :id="id" @hidden="cancelDeletion" @ok="confirmDeletion" :title="title" :ok-title="title" header-bg-variant="danger" header-text-variant="light" ok-variant="danger">
    <p>You will {{ removeWord }} the <slot/>. Are you sure?</p>
  </b-modal>
</template>

<script>
export default {
  name: 'deletion',
  props: {
    id: String,
    title: String,
    removeWord: {
      type: String,
      default: 'remove'
    }
  },
  methods: {
    confirmDeletion () {
      this.$emit('deletion')
    },
    cancelDeletion () {
      this.$emit('cancel')
    }
  }
}
</script>
