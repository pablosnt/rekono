<template>
  <div>
    <TableHeader :filters="filters" add="add-member-modal" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="usersFields" :items="users">
      <template #cell(role)="row">
        <b-badge :variant="roles[row.item.role.toLowerCase()]"><strong>{{ row.item.role.toUpperCase() }}</strong></b-badge>
      </template>
      <template #cell(last_login)="row">
        {{ row.item.last_login !== null ? row.item.last_login.split('.', 1)[0].replace('T', ' ') : '' }}
      </template>
      <template #cell(actions)="row">
        <b-button variant="outline" @click="selectUser(row.item)" v-b-modal.delete-member-modal v-b-tooltip.hover title="Remove Member" :disabled="row.item.id === $store.state.user">
          <b-icon variant="danger" icon="trash-fill"/>
        </b-button>
      </template>
    </b-table>
    <Pagination :page="page" :limit="limit" :limits="limits" :total="total" name="members" @pagination="pagination"/>
    <Deletion id="delete-member-modal"
      title="Delete Member"
      @deletion="deleteMember"
      @clean="cleanSelection"
      v-if="selectedUser !== null">
      <span><strong>{{ selectedUser.username }}</strong> member</span>
    </Deletion>
    <ProjectMemberForm id="add-member-modal" :projectId="$route.params.id" @confirm="confirm"/>
  </div>
</template>

<script>
import UsersApi from '@/backend/users'
import ProjectsApi from '@/backend/projects'
import { roles, rolesByVariant } from '@/backend/constants'
import Deletion from '@/common/Deletion.vue'
import TableHeader from '@/common/TableHeader.vue'
import Pagination from '@/common/Pagination.vue'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import PaginationMixin from '@/common/mixin/PaginationMixin.vue'
import ProjectMemberForm from '@/modals/ProjectMemberForm.vue'
export default {
  name: 'projectMembersPage',
  mixins: [AlertMixin, PaginationMixin],
  props: {
    project: Object
  },
  data () {
    return {
      roles: rolesByVariant,
      users: this.fetchData(),
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
    ProjectMemberForm
  },
  watch: {
    users () {
      this.filters = [
        { name: 'Role', values: roles, valueField: 'value', textField: 'value', filterField: 'role' }
      ]
    }
  },
  methods: {
    fetchData (filters = null) {
      if (!filters) {
        filters = {}
      }
      filters.project = this.$route.params.id
      UsersApi.getAllUsers(this.getPage(), this.getLimit(), filters)
        .then(data => {
          this.total = data.count
          this.users = data.results
        })
    },
    deleteMember () {
      ProjectsApi.deleteMember(this.$route.params.id, this.selectedUser.id)
        .then(() => {
          this.$bvModal.hide('delete-member-modal')
          this.warning(`${this.selectedUser.username}`, 'Member deleted successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(`${this.selectedUser.username}`, 'Unexpected error in member deletion')
        })
    },
    selectUser (user) {
      this.selectedUser = user
    },
    cleanSelection () {
      this.selectedUser = null
    }
  }
}
</script>
