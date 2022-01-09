<template>
  <b-modal :id="id" @close="clean" @hidden="clean" @ok="confirm" :ok-title="okTitle" header-bg-variant="light" header-text-variant="info" ok-variant="info" size="lg">
    <template #modal-title>
      <b-link class="mr-2" :href="defectDojo" target="_blank">
        <b-img src="/static/defect-dojo-favicon.ico" width="30" height="30"/>
      </b-link>
      Defect-Dojo Import
    </template>
    <b-alert v-model="alreadyReported" variant="warning">
      <b-icon class="mr-2" icon="exclamation-circle-fill" variant="warning"/>
      <span v-if="!isFinding">This execution has already been reported to Defect-Dojo</span>
      <span v-if="isFinding">This finding has already been reported to Defect-Dojo</span>
    </b-alert>
    The import will be performed in the associated Defect-Dojo product to the Rekono project. You can choose an existing engagement or creating new one before import findings
    <b-form class="mt-2">
      <b-tabs active-nav-item-class="text-info" align="center" @input="changeTab">
        <b-tab title="Create Engagement" title-link-class="text-secondary">
          <b-form-group class="mt-3" description="Engagement name" invalid-feedback="Engagement name is required">
            <b-form-input type="text" v-model="engagementName" :state="nameState"/>
          </b-form-group>
          <b-form-group description="Engagement description" invalid-feedback="Engagement description is required">
            <b-form-textarea v-model="engagementDescription" :state="descriptionState" rows="4"/>
          </b-form-group>
        </b-tab>
        <b-tab title="Select Engagement" title-link-class="text-secondary">
          <b-form-group class="mt-3" description="Engagement Id" invalid-feedback="Engagement Id is required">
            <b-form-input v-model="engagementId" :state="idState" type="number"/>
          </b-form-group>
        </b-tab>
      </b-tabs>
    </b-form>
    <b-container v-if="!isFinding">
      <hr/>
      <b-row align-v="top">
        <b-col cols="8">
          <b-form-group>
             <b-form-checkbox v-model="importFindings">Import Rekono findings instead of original tool output</b-form-checkbox>
           </b-form-group>
        </b-col>
        <b-col>
          <b-button variant="outline" v-b-toggle.dd-recomendation v-b-tooltip.hover title="Help me!">
            <b-icon variant="info" icon="question-circle-fill"/>
          </b-button>
        </b-col>
      </b-row>
      <b-collapse id="dd-recomendation">
        <p class="text-muted">You can import the original tool output or the findings parsed by Rekono. It's recommended to import the original tool output, except for Defect-Dojo unsupported tools</p>
      </b-collapse>
    </b-container>
  </b-modal>
</template>

<script>
import DefectDojoApi from '@/backend/defect-dojo.js'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
export default {
  name: 'defectDojoForm',
  mixins: [AlertMixin],
  props: ['id', 'path', 'itemId', 'alreadyReported'],
  computed: {
    isFinding () {
      return (this.path !== 'tasks' && this.path !== 'executions' && this.path !== 'projects')
    },
    okTitle () {
      if (!this.isFinding && !this.importFindings) {
        return 'Import scans'
      } else if (!this.isFinding) {
        return 'Import findings'
      } else {
        return 'Import finding'
      }
    }
  },
  data () {
    return {
      defectDojo: process.env.VUE_APP_DEFECTDOJO_HOST,
      engagementId: null,
      engagementName: null,
      engagementDescription: null,
      idState: null,
      nameState: null,
      descriptionState: null,
      importFindings: false,
      currentTab: null
    }
  },
  methods: {
    changeTab (index) {
      this.currentTab = index
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        const element = (!this.isFinding && !this.importFindings) ? 'Scans' : 'Findings'
        this.defectDojoImport()
          .then(() => {
            this.success('Defect-Dojo', `${element} imported successfully in Defect-Dojo`)
            this.clean()
          })
          .catch(() => {
            this.danger('Defect-Dojo', `Unexpected error in ${element.toLowerCase()} import`)
            this.idState = null
            this.nameState = null
            this.descriptionState = null
          })
      }
    },
    check () {
      if (this.currentTab === 0) {
        this.engagementId = null
        this.nameState = (this.engagementName && this.engagementName.length > 0)
        this.descriptionState = (this.engagementDescription && this.engagementDescription.length > 0)
        return this.nameState && this.descriptionState
      } else if (this.currentTab === 1) {
        this.engagementName = null
        this.engagementDescription = null
        this.idState = (this.engagementId && this.engagementId > 0)
        return this.idState
      }
    },
    defectDojoImport () {
      if (this.isFinding) {
        return DefectDojoApi.importFinding(this.path, this.itemId, this.engagementId, this.engagementName, this.engagementDescription)
      } else if (this.importFindings) {
        return DefectDojoApi.importFindings(this.path, this.itemId, this.engagementId, this.engagementName, this.engagementDescription)
      } else {
        return DefectDojoApi.importScans(this.path, this.itemId, this.engagementId, this.engagementName, this.engagementDescription)
      }
    },
    clean () {
      this.engagementId = null
      this.engagementName = null
      this.engagementDescription = null
      this.idState = null
      this.nameState = null
      this.descriptionState = null
      this.importFindings = false
      this.$emit('clean')
    }
  }
}
</script>