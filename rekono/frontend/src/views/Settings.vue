<template>
    <b-form ref="settings_form" @submit="handleSettings">
        <b-row class="mr-4 ml-4 mb-5 mt-4" align-h="between">
            <b-col md="8" offset-md="2">
                <b-card>
                    <template #header>
                        <v-icon fill="dodgerblue" name="brands/telegram"/>
                        <strong class="ml-2 mr-2">Telegram Bot</strong>
                    </template>
                    <b-form-input type="password" v-model="settings[2]" placeholder="Telegram token"/>
                </b-card>
                <br/>
                <b-card>
                    <template #header>
                        <b-img src="/static/defect-dojo-favicon.ico" width="20" height="20"/>
                        <strong class="ml-2 mr-2">Defect-Dojo</strong>
                    </template>
                    <b-form-input type="text" v-model="settings[3]" placeholder="Defect-Dojo URL"/>
                    <b-form-input type="password" v-model="settings[4]" placeholder="Defect-Dojo API key"/>
                    <b-form-checkbox v-model="settings[5]">Defect-Dojo TLS verification</b-form-checkbox>
                    <b-form-input type="text" v-model="settings[6]" placeholder="Defect-Dojo tag"/>
                    <b-form-input type="text" v-model="settings[7]" placeholder="Defect-Dojo product type"/>
                    <b-form-input type="text" v-model="settings[8]" placeholder="Defect-Dojo test type"/>
                    <b-form-input type="text" v-model="settings[9]" placeholder="Defect-Dojo test"/>
                </b-card>
                <br/>
                <b-card>
                    <template #header>
                        <b-icon icon="shield-lock-fill" variant="danger"/>
                        <strong class="ml-2 mr-2">Security</strong>
                    </template>
                    <b-input-group :prepend="settings[1]">
                        <b-form-input v-model="settings[1]" type="range" min="100" max="1000"/>
                    </b-input-group>
                </b-card>
            </b-col>
        </b-row>
        <b-row class="mt-3" align-h="center">
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
        changes: [],
        settings: {
            1: null,
            2: null,
            3: null,
            4: null,
            5: null,
            6: null,
            7: null,
            8: null,
            9: null
        }
    }
  },
  methods: {
    getSettings () {
        this.getAllPages('/api/settings/')
            .then(results => {
                console.log(results)
                for (var index in results) {
                    this.settings[results[index].id] = results[index].value
                }
            })
    },
    handleSettings () {
        console.log(this.settings)
    },
    settingsChanged (id) {
        this.changes.push(id)
    }
  }
}
</script>