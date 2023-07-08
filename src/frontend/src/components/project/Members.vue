<template>
  <div>
    <table-header :filters="filters" add="add-member-modal" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="usersFields" :items="data">
      <template #cell(role)="row">
        <b-badge :variant="roleByVariant[row.item.role.toLowerCase()]"><strong>{{ row.item.role.toUpperCase() }}</strong></b-badge>
      </template>
      <template #cell(last_login)="row">
        {{ row.item.last_login !== null ? row.item.last_login.split('.', 1)[0].replace('T', ' ') : '' }}
      </template>
      <template #cell(actions)="row">
        <b-button variant="outline" @click="selectedUser = row.item" v-b-modal.delete-member-modal v-b-tooltip.hover title="Remove Member" :disabled="row.item.id === $store.state.user">
          <b-icon variant="danger" icon="trash-fill"/>
        </b-button>
      </template>
    </b-table>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="members" @pagination="pagination"/>
    <deletion id="delete-member-modal" title="Delete Member" @deletion="deleteMember" @clean="selectedUser = null" v-if="selectedUser !== null">
      <span><strong>{{ selectedUser.username }}</strong> member</span>
    </deletion>
    <project-member id="add-member-modal" :projectId="$route.params.id" @confirm="confirm"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import Pagination from '@/common/Pagination'
import TableHeader from '@/common/TableHeader'
import ProjectMember from '@/modals/ProjectMember'
export default {
  name: 'projectMembersPage',
  mixins: [RekonoApi],
  props: {
    project: Object
  },
  data () {
    this.fetchData()
    return {
      data: [],
      usersFields: [
        { key: 'first_name', sortable: true },
        { key: 'last_name', sortable: true },
        { key: 'username', sortable: true },
        { key: 'email', sortable: true },
        { key: 'role', sortable: true },
        { key: 'last_login', sortable: true },
        { key: 'actions', sortable: false }
      ],
      selectedUser: null,
      filters: []
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    ProjectMember
  },
  watch: {
    data () {
      this.filters = [
        { name: 'Role', values: this.roles, valueField: 'value', textField: 'value', filterField: 'role' }
      ]
    }
  },
  methods: {
    fetchData (params = {}) {
      params.project = this.$route.params.id
      params.o = 'username'
      return this.getOnePage('/api/users/', params)
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    deleteMember () {
      this.delete(`/api/projects/${this.$route.params.id}/members/${this.selectedUser.id}/`, this.selectedUser.username, 'Member deleted successfully').then(() => this.fetchData())
    }
  }
}
</script>
