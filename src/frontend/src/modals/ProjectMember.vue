<template>
  <b-modal :id="id" @show="fetchUsers" @hidden="clean" @ok="confirm" title="Add Member" ok-title="Add Member" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="add_member_form">
      <b-form-group invalid-feedback="User is required">
        <b-form-select v-model="member" :options="users" value-field="id" text-field="username" :state="memberState">
          <template #first>
            <b-form-select-option :value="null">Select an user</b-form-select-option>
          </template>
        </b-form-select>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'addProjectMemberModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    projectId: [Number, String]
  },
  data () {
    this.fetchUsers()
    return {
      users: [],
      member: null,
      memberState: null
    }
  },
  watch: {
    initialized (initialized) {
      if (initialized) {
        this.fetchUsers()
      }
    }
  },
  methods: {
    fetchUsers () {
      this.getAllPages('/api/users/', { project__ne: this.projectId, o: 'username' }).then(results => this.users = results)
    },
    check () {
      this.memberState = (this.member !== null)
      return this.memberState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.post(`/api/projects/${this.projectId}/members/`, { user: this.member }, 'New member', 'New member added successfully')
          .then(() => { return Promise.resolve(true) })
          .catch(() => { return Promise.resolve(false) })
          .then(success => { this.$emit('confirm', { id: this.id, success: success, reload: true }) })
      }
    },
    clean () {
      this.member = null
      this.memberState = null
    }
  }
}
</script>
