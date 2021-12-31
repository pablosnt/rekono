
<script>
export default {
  name: 'paginationMixin',
  data () {
    return {
      page: 1,
      limit: 25,
      limits: [25, 50, 100],
      total: 0
    }
  },
  methods: {
    getPage () {
      return this.page ? this.page : 1
    },
    getLimit () {
      return this.limit ? this.limit : 25
    },
    pagination (pagination) {
      this.page = pagination.page
      this.limit = pagination.limit
      this.fetchData(pagination.page, pagination.limit)
    },
    confirm (operation) {
      if (operation.success) {
        this.$bvModal.hide(operation.id)
        if (operation.reload) {
          this.fetchData()
        }
      }
    }
  }
}
</script>
