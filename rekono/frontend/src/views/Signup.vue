<template>
  <public-form>
    <template>
      <b-alert v-model="invalidToken" variant="danger">
          <b-icon icon="exclamation-circle-fill" variant="danger"></b-icon>
          Invalid OTP token
        </b-alert>
      <b-form @submit="handleSignup">
        <b-form-group :invalid-feedback="invalidUsername">
          <b-form-input type="text" v-model="username" :state="usernameState" placeholder="Username"/>
        </b-form-group>
        <b-form-group :invalid-feedback="invalidFirstName">
          <b-form-input type="text" v-model="firstName" :state="firstNameState" placeholder="First name"/>
        </b-form-group>
        <b-form-group :invalid-feedback="invalidLastName">
          <b-form-input type="text" v-model="lastName" :state="lastNameState" placeholder="Last name"/>
        </b-form-group>
        <b-form-group :invalid-feedback="invalidPassword">
          <b-form-input type="password" v-model="password" :state="passwordState" placeholder="Password"/>
        </b-form-group>
        <b-form-group :invalid-feedback="invalidPasswordConfirm">
          <b-form-input type="password" v-model="passwordConfirm" :state="passwordState" placeholder="Confirm password"/>
        </b-form-group>
        <b-row>
          <b-col cols="6">
            <b-link @click="$store.dispatch('redirectToLogin')">Already have an account?</b-link>
          </b-col>
          <b-col cols="6">
            <b-button type="submit" variant="dark" size="lg">Signup</b-button>
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
  name: 'signupPage',
  mixins: [RekonoApi],
  props: ['otp'],
  data () {
    return {
      username: null,
      firstName: null,
      lastName: null,
      password: null,
      passwordConfirm: null,
      usernameState: null,
      firstNameState: null,
      lastNameState: null,
      passwordState: null,
      invalidUsername: 'Username is required',
      invalidFirstName: 'First name is required',
      invalidLastName: 'Last name is required',
      invalidPassword: 'Password is required',
      invalidPasswordConfirm: 'Password confirmation is required',
      invalidToken: false
    }
  },
  components: {
    PublicForm
  },
  watch: {
    otp (otp) {
      this.checkOtp(otp)
    }
  },
  methods: {
    handleSignup (event) {
      event.preventDefault()
      if (this.check()) {
        this.post(
          '/api/users/create/',
          { username: this.username, first_name: this.firstName, last_name: this.lastName, password: this.password, otp: this.otp },
          this.username, 'User created successfully', false, null, true
        )
          .then(() => this.$store.dispatch('redirectToLogin'))
          .catch(error => {
            if (error.response.status === 401) {
              this.invalidToken = true
            }
          })
      }
    },
    checkOtp (otp) {
      if (!otp || otp.length === 0) {
        this.$store.dispatch('redirectToLogin')
      }
    },
    check () {
      this.checkOtp(this.otp)
      if (!this.validateName(this.username)) {
        this.usernameState = false
        this.invalidUsername = this.username && this.username.length > 0 ? 'Invalid username' : 'Username is required'
      }
      if (!this.validateName(this.firstName)) {
        this.firstNameState = false
        this.invalidFirstName = this.firstName && this.firstName.length > 0 ? 'Invalid first name' : 'First name is required'
      }
      if (!this.validateName(this.lastName)) {
        this.lastNameState = false
        this.invalidLastName = this.lastName && this.lastName.length > 0 ? 'Invalid last name' : 'Last name is required'
      }
      if (!this.password || this.password.length === 0 || this.password !== this.passwordConfirm) {
        this.passwordState = false
        this.invalidPassword = this.password && this.password.length > 0 ? "Password doesn't match confirmation" : 'Password is required'
        this.invalidPasswordConfirm = this.passwordConfirm && this.passwordConfirm.length > 0 ? "Password doesn't match confirmation" : 'Password confirmation is required'
      }
      return this.usernameState !== false && this.firstNameState !== false && this.lastNameState !== false && this.passwordState !== false
    }
  }
}
</script>
