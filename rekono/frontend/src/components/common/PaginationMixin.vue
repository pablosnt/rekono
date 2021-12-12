
<script>
export default {
  name: 'paginationMixin',
  data () {
    return {
      page: 1,
      size: 25,
      sizes: [25, 50, 100],
      total: 0
    }
  },
  methods: {
    pagination (pagination) {
      this.page = pagination.page
      this.size = pagination.size
      this.fetchData(pagination.page, pagination.size)
    },
    confirm (operation) {
      if (operation.success) {
        this.$bvModal.hide(operation.id)
        if (operation.reload) {
          this.fetchData(this.page, this.size)
        }
      }
    }
  }
}
</script>
