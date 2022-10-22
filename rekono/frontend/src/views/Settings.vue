<template>
    <b-form ref="settings_form" @submit="handleSettings">
        <b-row class="mr-4 ml-4 mb-4 mt-4" align-h="between">
            <b-col md="8" offset-md="2">
                <b-card>
                    <template #header>
                        <v-icon fill="dodgerblue" name="brands/telegram"/>
                        <strong class="ml-2 mr-2">Telegram Bot</strong>
                    </template>
                    <b-form-input type="password" v-model="telegramBotToken" placeholder="Telegram token" @change="telegramBotTokenChanged = true"/>
                </b-card>
                <br/>
                <b-card>
                    <template #header>
                        <b-img src="/static/defect-dojo-favicon.ico" width="20" height="20"/>
                        <strong class="ml-2 mr-2">Defect-Dojo</strong>
                    </template>
                    <b-form-input type="text" v-model="defectDojoUrl" placeholder="Defect-Dojo URL"/>
                    <b-form-input type="password" v-model="defectDojoApiKey" placeholder="Defect-Dojo API key"  @change="telegramBotTokenChanged = true"/>
                    <b-form-checkbox v-model="defectDojoVerifyTls">Defect-Dojo TLS verification</b-form-checkbox>
                    <b-form-input type="text" v-model="defectDojoTag" placeholder="Defect-Dojo tag"/>
                    <b-form-input type="text" v-model="defectDojoProductType" placeholder="Defect-Dojo product type"/>
                    <b-form-input type="text" v-model="defectDojoTestType" placeholder="Defect-Dojo test type"/>
                    <b-form-input type="text" v-model="defectDojoTest" placeholder="Defect-Dojo test"/>
                </b-card>
                <br/>
                <b-card>
                    <template #header>
                        <b-icon icon="shield-lock-fill" variant="danger"/>
                        <strong class="ml-2 mr-2">Security</strong>
                    </template>
                    <b-input-group :prepend="uploadFilesMaxMb">
                        <b-form-input v-model="uploadFilesMaxMb" type="range" min="128" max="1024"/>
                    </b-input-group>
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
    this.getSettings()
    return {
        uploadFilesMaxMb: null,
        telegramBotName: null,
        telegramBotToken: null,
        telegramBotTokenChanged: false,
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