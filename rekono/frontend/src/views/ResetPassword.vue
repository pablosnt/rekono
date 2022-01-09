<template>
  <PublicForm>
    <template>
      <b-form @submit="handleResetPassword">
        <b-alert v-if="!otp" v-model="emailSent" variant="success">
          <b-icon icon="check-circle-fill" variant="success"/>
          Done! You will receive an email with a<br/> temporal link to change your password
        </b-alert>
        <b-form-group v-if="!otp" invalid-feedback="Email is required">
          <b-input-group size="lg" class="mb-3">
            <b-input-group-prepend is-text>
              <b-icon icon="at"/>
            </b-input-group-prepend>
            <b-form-input type="email" v-model="email" placeholder="Email" :state="emailState" max-length="150" autofocus/>
          </b-input-group>
        </b-form-group>
        <b-form-group v-if="otp" invalid-feedback="Password is required">
          <b-input-group size="lg" class="mb-3">
            <b-input-group-prepend is-text>
              <b-icon icon="key-fill"/>
            </b-input-group-prepend>
            <b-form-input type="password" v-model="password" placeholder="Password" :state="passwordState"/>
          </b-input-group>
        </b-form-group>
        <b-form-group v-if="otp" invalid-feedback="Password is required">
          <b-input-group size="lg" class="mb-3">
            <b-input-group-prepend is-text>
              <b-icon icon="key-fill"/>
            </b-input-group-prepend>
            <b-form-input type="password" v-model="passwordConfirm" placeholder="Confirm password" :state="passwordState"/>
          </b-input-group>
        </b-form-group>
        <b-row>
          <b-col cols="6">
            <b-link @click="$store.dispatch('redirectToLogin')">Back to Login</b-link>
          </b-col>
          <b-col cols="6">
            <b-button type="submit" variant="dark" size="lg">Reset Password</b-button>
          </b-col>
        </b-row>
      </b-form>
    </template>
  </PublicForm>
</template>

<script>
import UsersApi from '@/backend/users'
import PublicForm from '@/common/PublicForm.vue'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
export default {
  name: 'resetPasswordForm',
  mixins: [AlertMixin],
  props: ['otp'],
  data () {
    return {
      email: null,
      emailState: null,
      emailSent: false,
      password: null,
      passwordConfirm: null,
      passwordState: null
    }
  },
  components: {
    PublicForm
  },
  methods: {
    handleResetPassword (event) {
      event.preventDefault()
      if (this.check()) {
        if (this.otp && this.otp.length > 0) {
          this.resetPassword()
        } else {
          this.requestResetPassword()
        }
      }
    },
    check () {
      if (this.otp && this.otp.length > 0) {
        this.passwordState = (this.password !== null && this.password.length > 0 && this.password === this.passwordConfirm)
        return this.passwordConfirm
      } else {
        this.emailState = (this.email !== null && this.email.length > 0)
        return this.emailState
      }
    },
    requestResetPassword () {
      UsersApi.requestResetPassword(this.email)
      this.emailSent = true
    },
    resetPassword () {
      UsersApi.resetPassword(this.password, this.otp)
        .then(() => {
          this.success('Reset Password', 'Password changed successfully')
          this.$store.dispatch('redirectToLogin')
        })
        .catch(() => {
          this.danger('Reset Password', 'Unexpected error in password change')
        })
    }
  }
}
</script>
