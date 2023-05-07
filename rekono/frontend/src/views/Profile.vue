<template>
  <div>
    <b-row class="mr-4 ml-4 mb-5 mt-4" align-h="between">
      <b-col cols="3">
        <b-row>
          <b-col align-self="center">
            <h2><strong>{{ username }}</strong></h2>
          </b-col>
          <b-col align-self="center">
            <b-badge :variant="roleByVariant[role.toLowerCase()]"><strong>{{ role.toUpperCase() }}</strong></b-badge>
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
      <b-row align-h="center">
        <b-col cols="4">
          <div class="mb-3" v-if="telegramBotName">
            <h4 v-if="telegramConfigured">
              <b-badge :href="telegramBotLink" target="blank" variant="outline">
                <b-icon variant="primary" icon="patch-check-fill"/>
                @{{ telegramBotName }} is linked!
              </b-badge>
            </h4>
            <b-card align="center" v-if="!telegramConfigured">
              <template #header>
                <b-button v-b-toggle.telegram-bot variant="outline" @click="showTelegramBot = !showTelegramBot">
                  <v-icon fill="dodgerblue" name="brands/telegram"/>
                  <strong class="ml-2 mr-2">Telegram Bot</strong>
                  <b-icon v-if="!showTelegramBot" variant="secondary" icon="caret-down-fill"/>
                  <b-icon v-if="showTelegramBot" variant="secondary" icon="caret-up-fill"/>
                </b-button>
              </template>
              <b-collapse id="telegram-bot">
                <div class="text-right">
                  <b-button v-b-toggle.telegram-steps @click="showTelegramSteps = !showTelegramSteps" variant="outline">
                    <b-icon v-if="!showTelegramSteps" variant="dark" icon="eye-fill"/>
                    <b-icon v-if="showTelegramSteps" variant="secondary" icon="eye-slash-fill"/>
                    Steps
                  </b-button>
                </div>
                <b-collapse id="telegram-steps" class="text-left">
                  <h4>Steps</h4>
                  <p>1. Go to <a :href="telegramBotLink" target="blank"><strong>{{ telegramBotName }}</strong></a></p>
                  <p>2. Send the <strong>/start</strong> message to the bot</p>
                  <p>3. <a :href="telegramBotLink" target="blank"><strong>{{ telegramBotName }}</strong></a> will send you a temporal token</p>
                  <p>4. Copy the token in this form</p>
                  <p>5. Now you can use the bot and receive notifications. Send the <strong>/help</strong> message to see the usage</p>
                </b-collapse>
                <b-form-group class="mt-4" invalid-description="Token is required">
                  <b-form-input type="password" v-model="telegramToken" placeholder="Telegram token" :state="telegramTokenState"/>
                </b-form-group>
              </b-collapse>
              <template #footer v-if="showTelegramBot">
                <b-button squared variant="primary" @click="handleTelegramToken">Link Telegram Bot</b-button>
              </template>
            </b-card>
          </div>
          <b-card class="mt-3 mb-3">
            <template #header>
              <b-button v-b-toggle.rekono-api variant="outline" @click="showRekonoApi = !showRekonoApi">
                <b-icon variant="danger" icon="code-slash"/>
                <strong class="ml-2 mr-2">Rekono API Rest</strong>
                <b-icon v-if="!showRekonoApi" variant="secondary" icon="caret-down-fill"/>
                <b-icon v-if="showRekonoApi" variant="secondary" icon="caret-up-fill"/>
              </b-button>
            </template>
            <b-collapse id="rekono-api">
              <b-card-text>
                <b-alert v-model="passwordError" variant="danger">
                  <b-icon icon="exclamation-circle-fill" variant="danger"></b-icon>
                  Invalid credentials
                </b-alert>
                <b-form @submit="handleGetApiKey">
                  <b-row align="start">
                    <b-col lg="9">
                      <b-form-input class="mr-2" type="password" v-model="password" :state="passwordState" placeholder="Password"/>
                    </b-col>
                    <b-col lg="3">
                      <b-button type="submit" variant="danger">API key</b-button>
                    </b-col>
                  </b-row>
                </b-form>
                <b-input-group class="mt-2">
                  <b-form-input type="password" v-model="apiKey" placeholder="API key" disabled/>
                  <template #append>
                    <b-button id="copy-api-key" :disabled="!apiKey" variant="outline-dark" v-b-hover="copyHover" v-clipboard="() => apiKey">
                      <b-icon v-if="!isCopyHover" variant="dark" icon="files"/>
                      <b-icon v-if="isCopyHover" variant="light" icon="files"/>
                    </b-button>
                    <b-tooltip target="copy-api-key" triggers="hover" title="Copy"/>
                    <b-tooltip v-if="isCopyHover" target="copy-api-key" triggers="click" title="Copied!"/>
                  </template>
                </b-input-group>
              </b-card-text>
            </b-collapse>
            <template #footer v-if="showRekonoApi">
                <b-link class="text-danger" :href="getUrl('/api/schema/swagger-ui.html')" target="_blank">API documentation</b-link>
              </template>
          </b-card>
          <b-row class="mt-3" align-h="center">
            <b-button squared v-b-modal.change-password-modal>Change Password</b-button>
            <change-password id="change-password-modal" :username="username"/>
          </b-row>
        </b-col>
        <b-col cols="7">
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
                    <v-icon fill="dodgerblue" name="brands/telegram"/>
                  </b-form-checkbox>
                </b-form-group>
              </b-col>
            </b-row>
          </b-card>
          <b-row class="mt-3" align-h="center">
            <b-button type="submit" variant="dark" size="lg">Save</b-button>
          </b-row>
        </b-col>
      </b-row>
    </b-form>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import ChangePassword from '@/modals/ChangePassword'
export default {
  name: 'profilePage',
  mixins: [RekonoApi],
  data () {
    this.getProfile()
    this.getSettings()
    return {
      showTelegramSteps: false,
      id: null,
      username: null,
      password: null,
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
      apiKey: null,
      firstNameState: null,
      lastNameState: null,
      telegramTokenState: null,
      passwordState: null,
      passwordError: false,
      showTelegramBot: false,
      showRekonoApi: false,
      isCopyHover: false
    }
  },
  components: {
    ChangePassword
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
    getProfile () {
      this.get('/api/profile/').then(response => { this.processData(response.data) }) 
    },
    handleUpdateProfile(event) {
      event.preventDefault()
      if (this.checkProfile) {
        this.put(
          '/api/profile/',
          { first_name: this.firstName, last_name: this.lastName, notification_scope: this.notificationScope, email_notification: this.emailNotification, telegram_notification: this.telegramNotification },
          this.username, 'Profile updated successfully'
        ).then(data => this.processData(data))
      }
    },
    checkProfile () {
      let valid = this.$refs.profile_form.checkValidity()
      this.firstNameState = (this.firstName && this.firstName.length > 0)
      this.lastNameState = (this.lastName && this.lastName.length > 0)
      return valid
    },
    handleTelegramToken (event) {
      event.preventDefault()
      if (this.checkTelegramToken()) {
        this.post('/api/profile/telegram-token/', { otp: this.telegramToken }, this.username, 'Telegram configured successfully', true, null, true)
          .then(() => { this.getProfile() })
          .catch(() => { this.danger(this.username, 'Invalid Telegram token') })
      }
    },
    checkTelegramToken () {
      this.telegramTokenState = (this.telegramToken && this.telegramToken.length > 0)
      return this.telegramTokenState
    },
    handleGetApiKey (event) {
      event.preventDefault()
      if (this.checkAPIKey() === null) {
        this.post('/api/api-token/', { username: this.username, password: this.password })
          .then(data => { this.apiKey = data.token; this.passwordError = false })
          .catch(() => { this.passwordError = true })
      }
    },
    checkAPIKey () {
      this.passwordState = (this.password === null || this.password.length === 0) ? false : null
      return this.passwordState
    },
    copyHover (hovered) {
      this.isCopyHover = hovered
    }
  }
}
</script>
