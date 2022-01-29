<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="Change Password" ok-title="Change Password" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-alert v-model="passwordError" variant="danger">
      <b-icon icon="exclamation-circle-fill" variant="danger"></b-icon>
      Invalid credentials
    </b-alert>
    <b-form ref="change_password_form">
      <b-form-group invalid-feedback="Old password is required">
        <b-form-input type="password" v-model="oldPassword" :state="oldPasswordState" placeholder="Old password"/>
      </b-form-group>
      <b-form-group invalid-feedback="New password is required">
        <b-form-input type="password" v-model="newPassword" :state="newPasswordState" placeholder="New password"/>
      </b-form-group>
      <b-form-group invalid-feedback="New password is required">
        <b-form-input type="password" v-model="passwordConfirm" :state="newPasswordState" placeholder="Confirm password"/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'changePasswordModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    username: String
  },
  data () {
    return {
      oldPassword: null,
      newPassword: null,
      passwordConfirm: null,
      oldPasswordState: null,
      newPasswordState: null,
      passwordError: false
    }
  },
  methods: {
    handleError (error, title) {
      if (error.response.status !== 401) {
        this.$parent.$options.methods.handleError(error, title)
      }
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.put('/api/profile/change-password/', { password: this.newPassword, old_password: this.oldPassword }, this.username, 'Password changed successfully')
          .catch(error => {
            if (error.response.status !== 401) {
              this.passwordError = true
            }
          })
      }
    },
    check () {
      const valid = this.$refs.change_password_form.checkValidity()
      this.oldPasswordState = (this.oldPassword && this.oldPassword.length > 0)
      this.newPasswordState = (this.newPassword && this.newPassword.length > 0 && this.newPassword === this.passwordConfirm)
      return valid && this.oldPasswordState && this.newPasswordState
    },
    clean () {
      this.oldPassword = null
      this.newPassword = null
      this.passwordConfirm = null
      this.oldPasswordState = null
      this.newPasswordState = null
    }
  }
}
</script>
