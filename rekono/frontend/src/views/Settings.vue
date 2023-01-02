<template>
    <b-form ref="settings_form" @submit="handleSettings">
        <b-row class="mr-4 ml-4 mb-4 mt-4" align-h="between">
            <b-col md="8" offset-md="2">
                <b-card>
                    <template #header>
                        <v-icon fill="dodgerblue" name="brands/telegram"/>
                        <strong class="ml-2 mr-2">Telegram Bot</strong>
                    </template>
                    <a v-if="telegramBotLink" :href="telegramBotLink" target="blank"><strong>@{{ telegramBotName }}</strong></a>
                    <a v-if="!telegramBotLink" href="https://core.telegram.org/bots#how-do-i-create-a-bot" target="blank">How can I get one token?</a>
                    <b-row class="mt-3 mb-3">
                        <b-col sm="3">
                            <label>Telegram token</label>
                        </b-col>
                        <b-col sm="9">
                            <b-form-input type="password" v-model="telegramBotToken" placeholder="Telegram token" @change="telegramBotTokenChanged = true" :state="telegramBotTokenState"/>
                        </b-col>
                    </b-row>
                </b-card>
                <br/>
                <b-card>
                    <template #header>
                        <b-img src="/static/defect-dojo-favicon.ico" width="20" height="20"/>
                        <strong class="ml-2 mr-2">Defect-Dojo</strong>
                    </template>
                    <b-row class="mb-3">
                        <b-col sm="2">
                            <label>URL</label>
                        </b-col>
                        <b-col sm="7">
                            <b-form-input type="text" v-model="defectDojoUrl" placeholder="Defect-Dojo URL" :state="defectDojoUrlState"/>
                        </b-col>
                        <b-col sm="3">
                            <b-icon icon="check-circle-fill" variant="success" v-if="defectDojoEnabled"/>
                            <b-icon icon="x-circle-fill" variant="danger" v-if="!defectDojoEnabled"/>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col sm="2">
                            <label>API key</label>
                        </b-col>
                        <b-col sm="7">
                            <b-form-input type="password" v-model="defectDojoApiKey" placeholder="Defect-Dojo API key"  @change="defectDojoApiKeyChanged = true" :state="defectDojoApiKeyState"/>
                        </b-col>
                        <b-col sm="3">
                            <b-form-checkbox v-model="defectDojoVerifyTls">TLS verification</b-form-checkbox>
                        </b-col>
                    </b-row>
                    <hr/>
                    <b-row>
                        <b-col lg="6">
                            <b-row class="mb-3">
                                <b-col sm="4">
                                    <label>Tag</label>
                                </b-col>
                                <b-col sm="8">
                                    <b-form-input type="text" v-model="defectDojoTag" placeholder="Defect-Dojo tag" :state="defectDojoTagState"/>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col sm="4">
                                    <label>Test type</label>
                                </b-col>
                                <b-col sm="8">
                                    <b-form-input type="text" v-model="defectDojoTestType" placeholder="Defect-Dojo test type" :state="defectDojoTestTypeState"/>
                                </b-col>
                            </b-row>
                        </b-col>
                        <b-col lg="6">
                            <b-row class="mb-3">
                                <b-col sm="4">
                                    <label>Product type</label>
                                </b-col>
                                <b-col sm="8">
                                    <b-form-input type="text" v-model="defectDojoProductType" placeholder="Defect-Dojo product type" :state="defectDojoProductTypeState"/>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col sm="4">
                                    <label>Test</label>
                                </b-col>
                                <b-col sm="8">
                                    <b-form-input type="text" v-model="defectDojoTest" placeholder="Defect-Dojo test" :state="defectDojoTestState"/>
                                </b-col>
                            </b-row>
                        </b-col>
                    </b-row>
                </b-card>
                <br/>
                <b-card>
                    <template #header>
                        <b-icon icon="shield-lock-fill" variant="danger"/>
                        <strong class="ml-2 mr-2">Security</strong>
                    </template>
                    <b-row>
                        <b-col sm="3">
                            <label>Max MB for uploaded files</label>
                        </b-col>
                        <b-col sm="9">
                            <b-input-group :prepend="uploadFilesMaxMb.toString()">
                                <b-form-input v-model="uploadFilesMaxMb" type="range" min="128" max="1024" :state="uploadFilesMaxMbState"/>
                            </b-input-group>
                        </b-col>
                    </b-row>
                </b-card>
            </b-col>
        </b-row>
        <b-row class="mb-3" align-h="center">
            <b-button type="submit" variant="dark" size="lg">Save</b-button>
        </b-row>
    </b-form>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi';
export default {
  name: 'settingsPage',
  mixins: [RekonoApi],
  data () {
    if (this.$store.state.role !== 'Admin') {
        this.$router.push('/')
    }
    this.getSettings()
    return {
        uploadFilesMaxMb: null,
        uploadFilesMaxMbState: null,
        telegramBotName: null,
        telegramBotToken: null,
        telegramBotTokenChanged: false,
        telegramBotTokenState: null,
        telegramBotLink: null,
        defectDojoUrl: null,
        defectDojoUrlState: null,
        defectDojoApiKey: null,
        defectDojoApiKeyChanged: false,
        defectDojoApiKeyState: null,
        defectDojoVerifyTls: null,
        defectDojoTag: null,
        defectDojoTagState: null,
        defectDojoProductType: null,
        defectDojoProductTypeState: null,
        defectDojoTestType: null,
        defectDojoTestTypeState: null,
        defectDojoTest: null,
        defectDojoTestState: null,
        defectDojoEnabled: null,
    }
  },
  methods: {
    processResponse (data) {
        this.uploadFilesMaxMb = data.upload_files_max_mb
        this.telegramBotName = data.telegram_bot_name
        this.telegramBotToken = data.telegram_bot_token
        this.telegramBotTokenChanged = false
        this.telegramBotLink = this.telegramBotName ? `https://t.me/${this.telegramBotName}` : null
        this.defectDojoUrl = data.defect_dojo_url
        this.defectDojoApiKey = data.defect_dojo_api_key
        this.defectDojoApiKeyChanged = false
        this.defectDojoVerifyTls = data.defect_dojo_verify_tls
        this.defectDojoTag = data.defect_dojo_tag
        this.defectDojoProductType = data.defect_dojo_product_type
        this.defectDojoTestType = data.defect_dojo_test_type
        this.defectDojoTest = data.defect_dojo_test
        this.defectDojoEnabled = data.defect_dojo_enabled
    },
    getSettings () {
        this.get('/api/system/1/').then(response => this.processResponse(response.data))
    },
    checkSettings () {
        this.defectDojoUrlState = null
        this.defectDojoTagState = null
        this.defectDojoProductTypeState = null
        this.defectDojoTestTypeState = null
        this.defectDojoTestState = null
        this.telegramBotTokenState = null
        this.defectDojoApiKeyState = null
        if (this.defectDojoUrl && !this.validateUrl(this.defectDojoUrl)) {
            this.defectDojoUrlState = false
        }
        if (!this.validateName(this.defectDojoTag)) {
            this.defectDojoTagState = false
        }
        if (!this.validateName(this.defectDojoProductType)) {
            this.defectDojoProductTypeState = false
        }
        if (!this.validateName(this.defectDojoTestType)) {
            this.defectDojoTestTypeState = false
        }
        if (!this.validateName(this.defectDojoTest)) {
            this.defectDojoTestState = false
        }
        if (this.telegramBotTokenChanged && this.telegramBotToken && !this.validateTelegramToken(this.telegramBotToken)) {
            this.telegramBotTokenState = false
        }
        if (this.defectDojoApiKeyChanged && this.defectDojoApiKey && !this.validateDefectDojoKey(this.defectDojoApiKey)) {
            this.defectDojoApiKeyState = false
        }
        return (this.defectDojoUrlState != false && this.defectDojoTagState != false && this.defectDojoProductTypeState != false && this.defectDojoTestTypeState != false && this.defectDojoTestState != false && this.telegramBotTokenState != false && this.defectDojoApiKeyState != false)
    },
    handleSettings (event) {
        event.preventDefault()
        if (this.checkSettings()) {
            let data = {
                upload_files_max_mb: this.uploadFilesMaxMb,
                defect_dojo_url: this.defectDojoUrl,
                defect_dojo_verify_tls: this.defectDojoVerifyTls,
                defect_dojo_tag: this.defectDojoTag,
                defect_dojo_product_type: this.defectDojoProductType,
                defect_dojo_test_type: this.defectDojoTestType,
                defect_dojo_test: this.defectDojoTest
            }
            if (this.telegramBotTokenChanged) {
                data.telegram_bot_token = this.telegramBotToken
            }
            if (this.defectDojoApiKeyChanged) {
                data.defect_dojo_api_key = this.defectDojoApiKey
            }
            this.put('/api/system/1/', data, 'Settings', 'Settings updated successfully')
                .then(data => this.processResponse(data))
        }
    }
  }
}
</script>