<template>
   <b-modal :id="id" @hidden="clean" @ok="confirm" title="New User" ok-title="Invite User" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="invite_user_form">
      <b-form-group invalid-feedback="User email is required">
        <b-input-group>
          <b-input-group-prepend is-text>
              <b-icon icon="at"/>
            </b-input-group-prepend>
          <b-form-input type="email" v-model="email" placeholder="Email" :state="emailState" max-length="150" autofocus required/>
        </b-input-group>
      </b-form-group>
      <b-form-group description="User role" invalid-feedback="User role is required">
        <b-form-select v-model="role" :options="roles" value-field="value" text-field="value" :state="roleState" required/>
      </b-form-group>
    </b-form>
   </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'inviteUserModal',
  mixins: [RekonoApi],
  props: ['id'],
  data () {
    return {
      email: null,
      role: null,
      emailState: null,
      roleState: null
    }
  },
  methods: {
    check () {
      const valid = this.$refs.invite_user_form.checkValidity()
      this.emailState = (this.email !== null && this.email.length > 0)
      this.roleState = (this.role !== null)
      return valid
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.post('/api/users/invite/', { email: this.email, role: this.role }, this.email, 'New user invited successfully')
          .then(() => this.$emit('confirm', { id: this.id, success: true, reload: true }))
      }
    },
    clean () {
      this.email = null
      this.role = null
      this.emailState = null
      this.roleState = null
    }
  }
}
</script>
