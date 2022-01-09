<template>
  <PublicForm>
    <template>
      <b-form @submit="handleSignup">
        <b-form-group invalid-feedback="Username is required">
          <b-form-input type="text" v-model="username" :state="usernameState" placeholder="Username"/>
        </b-form-group>
        <b-form-group invalid-feedback="First name is required">
          <b-form-input type="text" v-model="firstName" :state="firstNameState" placeholder="First name"/>
        </b-form-group>
        <b-form-group invalid-feedback="Last name is required">
          <b-form-input type="text" v-model="lastName" :state="lastNameState" placeholder="Last name"/>
        </b-form-group>
        <b-form-group invalid-feedback="Password is required">
          <b-form-input type="password" v-model="password" :state="passwordState" placeholder="Password"/>
        </b-form-group>
        <b-form-group invalid-feedback="Password is required">
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
  </PublicForm>
</template>

<script>
import UsersApi from '@/backend/users'
import PublicForm from '@/common/PublicForm.vue'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
export default {
  name: 'signupForm',
  mixins: [AlertMixin],
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
      passwordState: null
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
        this.signup()
      }
    },
    checkOtp (otp) {
      if (!otp || otp.length === 0) {
        this.$store.dispatch('redirectToLogin')
      }
    },
    check () {
      this.checkOtp(this.otp)
      this.usernameState = (this.username !== null && this.username.length > 0)
      this.firstNameState = (this.firstName !== null && this.firstName.length > 0)
      this.lastNameState = (this.lastName !== null && this.lastName.length > 0)
      this.passwordState = (this.password && this.password.length > 0 && this.password === this.passwordConfirm)
      return this.usernameState && this.firstNameState && this.lastNameState && this.passwordState
    },
    signup () {
      UsersApi.createUser(this.username, this.firstName, this.lastName, this.password, this.otp)
        .then(() => {
          this.success(this.username, 'User created successfully')
          this.$store.dispatch('redirectToLogin')
        })
        .catch(() => {
          this.danger(this.username, 'Unexpected error in user creation')
        })
    }
  }
}
</script>
