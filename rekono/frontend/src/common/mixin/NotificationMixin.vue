
<script>
export default {
  name: 'notificationMixin',
  methods: {
    notification (title, body, variant) {
    this.$bvToast.toast(body, {
      title: title,
      variant: variant,
      solid: true
    })
    },
    success (title, body) {
      this.notification(title, body, 'success')
    },
    warning (title, body) {
      this.notification(title, body, 'warning')
    },
    danger (title, body) {
      this.notification(title, body, 'danger')
    }
  }
}
</script>
