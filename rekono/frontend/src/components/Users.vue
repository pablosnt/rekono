<template>
  <div>
    <TableHeader :filters="filters" add="invite-modal" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="usersFields" :items="users">
      <template #cell(role)="row">
        <b-form-select v-if="row.item.is_active" v-model="row.item.role" :options="roles" value-field="value" text-field="value" :disabled="row.item.id === $store.state.user" @input="selectUser(row.item)" @change="updateRole"/>
        <b-form-select v-if="!row.item.is_active" v-model="row.item.role" :options="roles" value-field="value" text-field="value" @change="selectRoleBeforeEnableUser"/>
      </template>
      <template #cell(last_login)="row">
        {{ row.item.last_login !== null ? row.item.last_login.split('.', 1)[0].replace('T', ' ') : '' }}
      </template>
      <template #cell(actions)="row">
        <b-button v-if="row.item.is_active" variant="outline" @click="selectUser(row.item)" v-b-modal.disable-user-modal v-b-tooltip.hover title="Disable User" :disabled="row.item.id === $store.state.user">
          <b-icon variant="danger" icon="dash-circle-fill"/>
        </b-button>
        <b-button v-if="!row.item.is_active" variant="outline" @click="selectAndEnableUser(row.item)" v-b-tooltip.hover title="Enable User">
          <b-icon variant="success" icon="check-circle-fill"/>
        </b-button>
      </template>
    </b-table>
    <Pagination :page="page" :limit="limit" :limits="limits" :total="total" name="users" @pagination="pagination"/>
    <Deletion id="disable-user-modal"
      title="Disable User"
      removeWord="disable"
      @deletion="disableUser"
      @clean="cleanSelection"
      v-if="selectedUser !== null">
      <span><strong>{{ selectedUser.username }}</strong> user</span>
    </Deletion>
    <UserInviteForm id="invite-modal" @confirm="confirm"/>
  </div>
</template>

<script>
import UsersApi from '@/backend/users'
import { roles } from '@/backend/constants'
import Deletion from '@/common/Deletion.vue'
import TableHeader from '@/common/TableHeader.vue'
import Pagination from '@/common/Pagination.vue'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import PaginationMixin from '@/common/mixin/PaginationMixin.vue'
import UserInviteForm from '@/modals/UserInviteForm.vue'
export default {
  name: 'usersPage',
  mixins: [AlertMixin, PaginationMixin],
  data () {
    return {
      roles: roles,
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
      selectedRole: null,
      filters: []
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    UserInviteForm
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
      UsersApi.getPaginatedUsers(this.getPage(), this.getLimit(), filters)
        .then(data => {
          this.total = data.count
          this.users = data.results
        })
    },
    updateRole (role) {
      UsersApi.updateRole(this.selectedUser.id, role)
        .then(() => {
          this.success(this.selectedUser.username, 'User role updated successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(this.selectedUser.username, 'Unexpected error in user role update')
        })
    },
    disableUser () {
      UsersApi.disableUser(this.selectedUser.id)
        .then(() => {
          this.warning(this.selectedUser.username, 'User disabled successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(this.selectedUser.username, 'Unexpected error in user disabling')
        })
    },
    enableUser () {
      UsersApi.enableUser(this.selectedUser.id, this.selectedRole)
        .then(() => {
          this.success(this.selectedUser.username, 'User enabled successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(this.selectedUser.username, 'Unexpected error in user enabling')
        })
    },
    selectAndEnableUser (user) {
      if (this.selectedRole) {
        this.selectUser(user)
        this.enableUser()
      } else {
        this.warning(user.username, 'Before enable this user, you need to select one role')
      }
    },
    selectRoleBeforeEnableUser (role) {
      this.selectedRole = role
    },
    selectUser (user) {
      this.selectedUser = user
    },
    cleanSelection () {
      this.selectedUser = null
      this.selectedRole = null
    }
  }
}
</script>

