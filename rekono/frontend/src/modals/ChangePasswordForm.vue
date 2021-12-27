<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="Change Password" ok-title="Change Password" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
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
import ProfileApi from '@/backend/profile'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
export default {
  name: 'changePasswordForm',
  mixins: [AlertMixin],
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
      newPasswordState: null
    }
  },
  methods: {
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.changePassword()
      }
    },
    check () {
      const valid = this.$refs.change_password_form.checkValidity()
      this.oldPasswordState = (this.oldPassword && this.oldPassword.length > 0)
      this.newPasswordState = (this.newPassword && this.newPassword.length > 0 && this.newPassword === this.passwordConfirm)
      return valid && this.oldPasswordState && this.newPasswordState
    },
    changePassword () {
      ProfileApi.changePassword(this.newPassword, this.oldPassword)
        .then(() => {
          this.success(this.username, 'Password changed successfully')
        })
        .catch(error => {
          console.log(typeof error)
          console.log(error.response.status)
          if (error.response.status === 401) {
            this.danger(this.username, 'Invalid password')
          } else {
            this.danger(this.username, 'Unexpected error in password change')
          }
        })
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
