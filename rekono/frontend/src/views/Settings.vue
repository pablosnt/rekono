<template>
    <b-form ref="settings_form" @submit="handleSettings">
        <b-row class="mr-4 ml-4 mb-4 mt-4" align-h="between">
            <b-col md="8" offset-md="2">
                <b-card>
                    <template #header>
                        <v-icon fill="dodgerblue" name="brands/telegram"/>
                        <strong class="ml-2 mr-2">Telegram Bot</strong>
                    </template>
                    <a v-if="telegramBotName" :href="telegramBotLink" target="blank"><strong>@{{ telegramBotName }}</strong></a>
                    <b-row class="mt-3">
                        <b-col sm="3">
                            <label>Telegram token</label>
                        </b-col>
                        <b-col sm="9">
                            <b-form-input type="password" v-model="telegramBotToken" placeholder="Telegram token" @change="telegramBotTokenChanged = true"/>
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
                            <b-form-input type="text" v-model="defectDojoUrl" placeholder="Defect-Dojo URL"/>
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
                            <b-form-input type="password" v-model="defectDojoApiKey" placeholder="Defect-Dojo API key"  @change="telegramBotTokenChanged = true"/>
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
                                    <b-form-input type="text" v-model="defectDojoTag" placeholder="Defect-Dojo tag"/>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col sm="4">
                                    <label>Test type</label>
                                </b-col>
                                <b-col sm="8">
                                    <b-form-input type="text" v-model="defectDojoTestType" placeholder="Defect-Dojo test type"/>
                                </b-col>
                            </b-row>
                        </b-col>
                        <b-col lg="6">
                            <b-row class="mb-3">
                                <b-col sm="4">
                                    <label>Product type</label>
                                </b-col>
                                <b-col sm="8">
                                    <b-form-input type="text" v-model="defectDojoProductType" placeholder="Defect-Dojo product type"/>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col sm="4">
                                    <label>Test</label>
                                </b-col>
                                <b-col sm="8">
                                    <b-form-input type="text" v-model="defectDojoTest" placeholder="Defect-Dojo test"/>
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
                            <b-input-group :prepend="uploadFilesMaxMb">
                                <b-form-input v-model="uploadFilesMaxMb" type="range" min="128" max="1024"/>
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
        telegramBotName: null,
        telegramBotToken: null,
        telegramBotTokenChanged: false,
        telegramBotLink: null,
        defectDojoUrl: null,
        defectDojoApiKey: null,
        defectDojoApiKeyChanged: false,
        defectDojoVerifyTls: null,
        defectDojoTag: null,
        defectDojoProductType: null,
        defectDojoTestType: null,
        defectDojoTest: null,
        defectDojoEnabled: null,
    }
  },
  methods: {
    processResponse (response) {
        this.uploadFilesMaxMb = response.data.upload_files_max_mb
        this.telegramBotName = response.data.telegram_bot_name
        this.telegramBotToken = response.data.telegram_bot_token
        this.telegramBotLink = this.telegramBotName ? `https://t.me/${this.telegramBotName}` : null
        this.defectDojoUrl = response.data.defect_dojo_url
        this.defectDojoApiKey = response.data.defect_dojo_api_key
        this.defectDojoVerifyTls = response.data.defect_dojo_verify_tls
        this.defectDojoTag = response.data.defect_dojo_tag
        this.defectDojoProductType = response.data.defect_dojo_product_type
        this.defectDojoTestType = response.data.defect_dojo_test_type
        this.defectDojoTest = response.data.defect_dojo_test
        this.defectDojoEnabled = response.data.defect_dojo_enabled
    },
    getSettings () {
        this.get('/api/system/1/').then(response => this.processResponse(response))
    },
    checkSettings () {
        return true
    },
    handleSettings (event) {
        event.preventDefault()
        if (this.checkSettings()) {
            var data = {
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
                .then(response => this.processResponse(response))
        }
    }
  }
}
</script>