
<script>
export default {
  name: 'alertMixin',
  methods: {
    alert (title, body, variant) {
      this.$bvToast.toast(body, {
        title: title,
        variant: variant,
        solid: true
      })
    },
    success (title, body) {
      this.alert(title, body, 'success')
    },
    warning (title, body) {
      this.alert(title, body, 'warning')
    },
    danger (title, body) {
      this.alert(title, body, 'danger')
    }
  }
}
</script>
