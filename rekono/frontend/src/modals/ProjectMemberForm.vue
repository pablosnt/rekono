<template>
  <b-modal :id="id" @show="fetchData" @hidden="clean" @ok="confirm" title="Add Member" ok-title="Add Member" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
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
import UsersApi from '@/backend/users'
import ProjectsApi from '@/backend/projects'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
export default {
  name: 'addProjectMemberForm',
  mixins: [AlertMixin],
  props: ['id', 'projectId'],
  data () {
    return {
      users: this.fetchData(),
      member: null,
      memberState: null
    }
  },
  watch: {
    initialized (initialized) {
      if (initialized) {
        this.fetchData()
      }
    }
  },
  methods: {
    fetchData () {
      UsersApi.getAllUsers({ project__ne: this.projectId }).then(results => { this.users = results })
    },
    check () {
      this.memberState = (this.member !== null)
      return this.memberState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.addMember().then(success => {
          this.$emit('confirm', { id: this.id, success: success, reload: true })
        })
      }
    },
    addMember () {
      return ProjectsApi.addMember(this.projectId, this.member)
        .then(() => {
          this.success('New member', 'New member added successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger('New member', 'Unexpected error in member addition')
          return Promise.resolve(false)
        })
    },
    clean () {
      this.member = null
      this.memberState = null
    }
  }
}
</script>
