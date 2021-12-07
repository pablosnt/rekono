<template>
  <b-modal :id="id" @hidden="cancelDeletion" @ok="confirmDeletion" :title="title" :ok-title="button" header-bg-variant="danger" header-text-variant="light" ok-variant="danger">
    <p>You will remove the <slot name="body"/>. Are you sure?</p>
  </b-modal>
</template>

<script>
export default {
  name: 'deleteConfirmation',
  props: ['id', 'title', 'button'],
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
