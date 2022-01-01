<template>
  <div>
    <b-row class="mr-4 ml-4 mb-5 mt-4" align-h="between">
      <b-col cols="2">
        <b-row>
          <b-col align-self="center">
            <h2><strong>{{ username }}</strong></h2>
          </b-col>
          <b-col align-self="center">
            <b-badge :variant="roles[role.toLowerCase()]"><strong>{{ role.toUpperCase() }}</strong></b-badge>
          </b-col>
        </b-row>
      </b-col>
      <b-col cols="3">
        <b-row>
          <b-col cols="4">
            <p class="text-dark">Joined at</p>
            <p class="text-dark">Last login</p>
          </b-col>
          <b-col cols="8">
              <p class="text-muted">{{ dateJoined !== null ? dateJoined.split('.', 1)[0].replace('T', ' ') : '' }}</p>
              <p class="text-muted">{{ lastLogin !== null ? lastLogin.split('.', 1)[0].replace('T', ' ') : '' }}</p>
          </b-col>
        </b-row>
      </b-col>
    </b-row>
    <b-form ref="profile_form" @submit="handleUpdateProfile">
      <b-row class="mb-3 ml-5 mr-5" align-h="end">
        <b-col cols="6">
          <b-form-group>
            <b-form-input v-model="firstName" :state="firstNameState" type="text" placeholder="First name"/>
          </b-form-group>
          <b-form-group>
            <b-form-input v-model="lastName" :state="lastNameState" type="text" placeholder="Last name"/>
          </b-form-group>
          <b-form-group>
            <b-form-input v-model="email" type="email" readonly/>
          </b-form-group>
          <b-card title="Notifications">
            <b-row align-h="center">
              <b-col cols="5">
                <b-form-group>
                  <b-form-select v-model="notificationScope" :options="notificationScopes" value-field="value" text-field="value"/>
                </b-form-group>
              </b-col>
              <b-col cols="6" class="text-left">
                <b-form-group>
                  <b-form-checkbox v-model="emailNotification">
                    Email
                    <b-icon variant="secondary" icon="envelope-fill"/>
                  </b-form-checkbox>
                </b-form-group>
                <b-form-group id="telegram-notification" v-b-tooltip.hover title="Configure your Telegram bot before enable notifications">
                  <b-form-checkbox v-model="telegramNotification" :disabled="!telegramConfigured">
                    Telegram Bot
                    <img src="/static/telegram.svg"/>
                  </b-form-checkbox>
                </b-form-group>
              </b-col>
            </b-row>
          </b-card>
          <b-row class="mt-3" align-h="center">
            <b-button type="submit" variant="dark" size="lg">Save</b-button>
          </b-row>
        </b-col>
        <b-col cols="4">
          <b-row class="mt-3" align-h="center">
            <h4 v-if="telegramConfigured">
              <b-badge variant="outline">
                <b-icon variant="success" icon="patch-check-fill"/>
                {{ telegramBot }} Bot is linked!
              </b-badge>
            </h4>
            <b-card align="center" v-if="!telegramConfigured">
              <template #header>
                <img src="/static/telegram.svg"/> <strong>Telegram Bot</strong>
              </template>
              <div class="text-right">
                <b-button v-b-toggle.telegram-steps @click="showTelegramSteps = !showTelegramSteps" variant="secondary">
                  <b-icon v-if="!showTelegramSteps" icon="eye-fill"/>
                  <b-icon v-if="showTelegramSteps" icon="eye-slash-fill"/>
                  Steps
                </b-button>
              </div>
              <b-collapse id="telegram-steps" class="text-left">
                <h4>Steps</h4>
                <p>1. Search the <strong>{{ telegramBot }}</strong> bot in Telegram</p>
                <p>2. Send the <strong>/start</strong> message to the bot</p>
                <p>3. <strong>{{ telegramBot }}</strong> will send you a temporal token</p>
                <p>4. Copy the token in this form</p>
                <p>5. Now you can use the bot and receive notifications. Send the <strong>/help</strong> message to see the usage</p>
              </b-collapse>
              <b-form-group class="mt-4" invalid-description="Token is required">
                <b-form-input type="password" v-model="telegramToken" placeholder="Telegram token" :state="telegramTokenState"/>
              </b-form-group>
              <template #footer>
                <b-button squared variant="primary" @click="handleTelegramToken">Link Telegram Bot</b-button>
              </template>
            </b-card>
          </b-row>
          <b-row class="mt-5" align-h="center">
            <b-button squared v-b-modal.change-password-modal>Change Password</b-button>
            <ChangePasswordForm id="change-password-modal" :username="username"/>
          </b-row>
        </b-col>
      </b-row>
    </b-form>
  </div>
</template>

<script>
import ProfileApi from '@/backend/profile'
import { notificationScopes, rolesByVariant } from '@/backend/constants'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import ChangePasswordForm from '@/modals/ChangePasswordForm.vue'
export default {
  name: 'profilePage',
  mixins: [AlertMixin],
  data () {
    this.fetchData()
    return {
      roles: rolesByVariant,
      telegramBot: process.env.VUE_APP_TELEGRAM_BOT,
      showTelegramSteps: false,
      notificationScopes: notificationScopes,
      id: null,
      username: null,
      firstName: null,
      lastName: null,
      email: null,
      dateJoined: null,
      lastLogin: null,
      role: 'Reader',
      telegramConfigured: null,
      notificationScope: null,
      emailNotification: null,
      telegramNotification: null,
      telegramToken: null,
      firstNameState: null,
      lastNameState: null,
      telegramTokenState: null
    }
  },
  components: {
    ChangePasswordForm
  },
  methods: {
    processData (data) {
      this.id = data.id
      this.username = data.username
      this.firstName = data.first_name
      this.lastName = data.last_name
      this.email = data.email
      this.dateJoined = data.date_joined
      this.lastLogin = data.last_login
      this.role = data.role
      this.telegramConfigured = data.telegram_configured
      this.notificationScope = data.notification_scope
      this.emailNotification = data.email_notification
      this.telegramNotification = data.telegram_notification
      if (this.telegramConfigured) {
        this.$root.$emit('bv::disable::tooltip', 'telegram-notification')
      }
    },
    fetchData () {
      ProfileApi.getProfile().then(data => {
        this.processData(data)
      }) 
    },
    handleUpdateProfile(event) {
      event.preventDefault()
      if (this.checkProfile) {
        this.updateProfile()
      }
    },
    checkProfile () {
      let valid = this.$refs.profile_form.checkValidity()
      this.firstNameState = (this.firstName && this.firstName.length > 0)
      this.lastNameState = (this.lastName && this.lastName.length > 0)
      return valid
    },
    updateProfile () {
      ProfileApi.updateProfile(this.firstName, this.lastName, this.notificationScope, this.emailNotification, this.telegramNotification)
        .then(data => {
          this.processData(data)
          this.success(this.username, 'Profile updated successfully')
        })
        .catch(() => {
          this.danger(this.username, 'Unexpected error in profile update')
        })
    },
    handleTelegramToken (event) {
      event.preventDefault()
      if (this.checkTelegramToken()) {
        this.configureTelegram()
      }
    },
    checkTelegramToken () {
      this.telegramTokenState = (this.telegramToken && this.telegramToken.length > 0)
      return this.telegramTokenState
    },
    configureTelegram () {
      ProfileApi.configureTelegram(this.telegramToken)
        .then(() => {
          this.success(this.username, 'Telegram configured successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(this.username, 'Unexpected error in telegram configuration')
        })
    }
  }
}
</script>
