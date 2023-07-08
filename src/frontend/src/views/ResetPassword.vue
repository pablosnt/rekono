<template>
  <public-form>
    <template>
      <b-form @submit="handleResetPassword">
        <b-alert v-if="!otp" v-model="emailSent" variant="success">
          <b-icon icon="check-circle-fill" variant="success"/>
          Done! You will receive an email with a<br/> temporal link to change your password
        </b-alert>
        <b-alert v-if="otp" v-model="passwordError" variant="danger">
          <b-icon icon="exclamation-circle-fill" variant="danger"></b-icon>
          {{ invalidPassword }}
        </b-alert>
        <b-form-group v-if="!otp" invalid-feedback="Email is required">
          <b-input-group size="lg" class="mb-3">
            <b-input-group-prepend is-text>
              <b-icon icon="at"/>
            </b-input-group-prepend>
            <b-form-input type="email" v-model="email" placeholder="Email" :state="emailState" max-length="150" autofocus/>
          </b-input-group>
        </b-form-group>
        <b-form-group v-if="otp">
          <b-input-group size="lg" class="mb-3">
            <b-input-group-prepend is-text>
              <b-icon icon="key-fill"/>
            </b-input-group-prepend>
            <b-form-input type="password" v-model="password" placeholder="Password" :state="passwordState"/>
          </b-input-group>
        </b-form-group>
        <b-form-group v-if="otp">
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
  </public-form>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import PublicForm from '@/common/PublicForm'
export default {
  name: 'resetPasswordPage',
  mixins: [RekonoApi],
  props: ['otp'],
  data () {
    return {
      email: null,
      emailState: null,
      emailSent: false,
      password: null,
      passwordConfirm: null,
      passwordState: null,
      passwordError: false,
      invalidPassword: 'Password is required'
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
          this.put('/api/reset-password/', { password: this.password, otp: this.otp }, 'Reset Password', 'Password changed successfully', false, null, true)
            .then(() => this.$store.dispatch('redirectToLogin'))
            .catch(error => {
              if (error.response.status === 401) {
                this.passwordError = true
                this.invalidPassword = 'Invalid OTP token'
              }
            })
        } else {
          this.post('/api/reset-password/', { email: this.email }, null, null, false)
          this.emailSent = true
        }
      }
    },
    check () {
      if (this.otp && this.otp.length > 0) {
        if (!this.password || this.password.length === 0 || this.password !== this.passwordConfirm) {
          this.passwordError = true
          this.passwordState = false
          this.invalidPassword = this.password && this.password.length > 0 ? "Password doesn't match confirmation" : 'Password is required'
        }
        return this.passwordState !== false
      } else {
        this.emailState = (this.email !== null && this.email.length > 0)
        return this.emailState
      }
    }
  }
}
</script>
