<template>
  <div>
    <table-header :filters="filters" add="invite-modal" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="usersFields" :items="data">
      <template #cell(role)="row">
        <b-form-select v-model="row.item.role" :options="roles" value-field="value" text-field="value" :disabled="row.item.id === $store.state.user" @input="selectedUser = row.item" @change="updateRole"/>
      </template>
      <template #cell(last_login)="row">
        {{ row.item.last_login !== null ? row.item.last_login.split('.', 1)[0].replace('T', ' ') : '' }}
      </template>
      <template #cell(actions)="row">
        <b-button v-if="row.item.is_active" variant="outline" @click="selectedUser = row.item" v-b-modal.disable-user-modal v-b-tooltip.hover title="Disable User" :disabled="row.item.id === $store.state.user">
          <b-icon variant="danger" icon="dash-circle-fill"/>
        </b-button>
        <b-button v-if="row.item.is_active === null" variant="outline" @click="selectedUser = row.item" v-b-modal.remove-user-modal v-b-tooltip.hover title="Remove User" :disabled="row.item.id === $store.state.user">
          <b-icon variant="danger" icon="trash-fill"/>
        </b-button>
        <b-button v-if="row.item.is_active === false" variant="outline" @click="enableUser(row.item)" v-b-tooltip.hover title="Enable User">
          <b-icon variant="success" icon="check-circle-fill"/>
        </b-button>
      </template>
    </b-table>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="users" @pagination="pagination"/>
    <deletion id="disable-user-modal" title="Disable User" removeWord="disable" @deletion="disableUser" @clean="selectedUser = null" v-if="selectedUser !== null">
      <span><strong>{{ selectedUser.username }}</strong> user</span>
    </deletion>
    <deletion id="remove-user-modal" title="Remove User" removeWord="remove" @deletion="disableUser" @clean="selectedUser = null" v-if="selectedUser !== null">
      <span><strong>{{ selectedUser.username }}</strong> user</span>
    </deletion>
    <invite-user id="invite-modal" @confirm="confirm"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import Pagination from '@/common/Pagination'
import TableHeader from '@/common/TableHeader'
import InviteUser from '@/modals/InviteUser'
export default {
  name: 'usersPage',
  mixins: [RekonoApi],
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
    InviteUser
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
      params.o = 'username'
      return this.getOnePage('/api/users/', params)
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    updateRole (role) {
      this.put(`/api/users/${this.selectedUser.id}/role/`, { role: role }, this.selectedUser.email, 'User role updated successfully')
    },
    disableUser () {
      this.delete(`/api/users/${this.selectedUser.id}/`, this.selectedUser.email, this.selectedUser.is_active ? 'User disabled successfully' : 'User removed successfully').then(() => this.fetchData())
    },
    enableUser (user) {
      this.post(`/api/users/${user.id}/enable/`, { }, user.email, 'User enabled successfully').then(() => this.fetchData())
    }
  }
}
</script>
