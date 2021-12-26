<template>
   <b-modal :id="id" @hidden="clean" @ok="confirm" title="New User" ok-title="Invite User" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="invite_user_form">
      <b-form-group invalid-feedback="User email is required">
        <b-input-group prepend="@">
          <b-form-input type="email" v-model="email" placeholder="Email" :state="emailState" autofocus required/>
        </b-input-group>
      </b-form-group>
      <b-form-group description="User role" invalid-feedback="User role is required">
        <b-form-select v-model="role" :options="roles" value-field="value" text-field="value" :state="roleState" required/>
      </b-form-group>
    </b-form>
    <template v-if="loading" #modal-ok>
      <b-button variant="dark" disabled>
        <b-spinner small></b-spinner>
      </b-button>
    </template>
   </b-modal>
</template>

<script>
import UsersApi from '@/backend/users'
import { roles } from '@/backend/constants'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
export default {
  name: 'inviteUserForm',
  mixins: [AlertMixin],
  props: ['id'],
  data () {
    return {
      roles: roles,
      email: null,
      role: null,
      emailState: null,
      roleState: null,
      loading: false
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
        this.loading = true
        this.invite().then(success => {
          this.$emit('confirm', { id: this.id, success: success, reload: true })
          this.loading = false
        })
      }
    },
    invite () {
      return UsersApi.inviteUser(this.email, this.role)
        .then(() => {
          this.success(this.email, 'New user invited successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.email, 'Unexpected error in user invitation')
          return Promise.resolve(false)
        })
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
