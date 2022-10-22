<template>
  <b-modal :id="id" @close="clean" @hidden="clean" @ok="confirm" ok-title="Update" header-bg-variant="light" header-text-variant="info" ok-variant="info" size="lg">
    <template #modal-title>
      <b-link class="mr-2" :href="defectDojoUrl" target="_blank">
        <b-img src="/static/defect-dojo-favicon.ico" width="30" height="30"/>
      </b-link>
      Defect-Dojo
    </template>
    <div class="text-left mb-4">
      <b-form-checkbox switch v-model="sync" size="md">Defect-Dojo synchronization. When an execution is completed, it will be imported in Defect-Dojo</b-form-checkbox>
    </div>
    <b-row class="mt-3">
      <b-col>
        <label>Product</label>
        <div class="text-muted mb-5">
          <b-form-checkbox switch v-model="autoProduct" size="md">Create a new product automatically</b-form-checkbox>
        </div>
        <b-form v-if="!autoProduct">
          <b-form-group description="Product Id">
            <b-form-input v-model="productId" :state="productIdState" type="number"/>
          </b-form-group>
        </b-form>
      </b-col>
      <b-col>
        <label>Engagement</label>
        <div class="text-muted mb-3">
          <b-form-checkbox switch v-model="autoEngagement" size="md">Create a new engagement for each target automatically</b-form-checkbox>
          <b-form-checkbox switch v-if="!autoEngagement" v-model="newEngagement" size="md">Create a new engagement for all targets</b-form-checkbox>
        </div>
        <b-form v-if="!autoEngagement && !newEngagement">
          <b-form-group description="Engagement Id">
            <b-form-input v-model="engagementId" :state="engagementIdState" type="number"/>
          </b-form-group>
        </b-form>
        <b-form v-if="!autoEngagement && newEngagement">
          <b-form-group class="mt-3" description="Engagement name" :invalid-feedback="invalidName">
            <b-form-input type="text" v-model="engagementName" :state="nameState" maxlength="100"/>
          </b-form-group>
          <b-form-group description="Engagement description" :invalid-feedback="invalidDescription">
            <b-form-textarea v-model="engagementDescription" :state="descriptionState" rows="4" maxlength="300"/>
          </b-form-group>
        </b-form>
      </b-col>
    </b-row>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'defectDojoModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    project: Object,
    initialized: {
      type: Boolean,
      default: false
    }
  },
  data () {
    this.getSettings()
    return {
      sync: null,
      autoProduct: null,
      autoEngagement: null,
      newEngagement: null,
      productId: null,
      engagementId: null,
      engagementName: null,
      engagementDescription: null,
      productIdState: null,
      engagementIdState: null,
      nameState: null,
      descriptionState: null,
      invalidName: 'Engagement name is required',
      invalidDescription: 'Engagement description is required',
    }
  },
  watch: {
    initialized (initialized) {
      if (initialized && this.project) {
        this.sync = this.project.defectdojo_synchronization
        this.autoProduct = false
        this.autoEngagement = this.project.defectdojo_engagement_by_target
        this.newEngagement = false
        this.productId = this.project.defectdojo_product_id
        this.engagementId = this.project.defectdojo_engagement_id
      }
    }
  },
  methods: {
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        let data = {}
        if (!this.autoProduct) {
          data.product_id = this.productId
        }
        if (!this.autoEngagement && !this.newEngagement) {
          data.engagement_id = this.engagementId
        } else if (!this.autoEngagement && this.newEngagement) {
          data.engagement_name = this.engagementName
          data.engagement_description = this.engagementDescription
        }
        this.put(`/api/projects/${this.project.id}/defect-dojo/`, data, 'Defect-Dojo', `Integration successfully configured for ${this.project.name}`)
          .then(() => {
            const confirmation = { id: this.id, success: true, reload: true }
            if (this.sync !== this.project.defectdojo_synchronization) {
              this.put(`/api/projects/${this.project.id}/defect-dojo/sync/`, { synchronization: this.sync }, 'Defect-Dojo', this.sync ? 'Synchronization has been enabled' : 'Synchronization has been disabled')
                .then(() => this.$emit('confirm', confirmation))
            } else {
              this.$emit('confirm', confirmation)
            }
          })
      }
    },
    check () {
      if (this.autoProduct) {
        this.productId = this.project.defectdojo_product_id
        this.productIdState = null
      } else {
        this.productIdState = (this.productId && this.productId > 0)
      }
      if (this.autoEngagement) {
        this.engagementId = this.project.defectdojo_engagement_id
        this.engagementName = null
        this.engagementDescription = null
        this.engagementIdState = null
        this.nameState = null
        this.descriptionState = null
      } else if (this.newEngagement) {
        this.engagementId = this.project.defectdojo_engagement_id
        this.engagementIdState = null
        this.nameState = this.validateName(this.engagementName)
        this.invalidName = this.engagementName && this.engagementName.length > 0 ? 'Invalid engagement name' : 'Engagement name is required'
        this.descriptionState = this.validateText(this.engagementDescription)
        this.invalidDescription = this.engagementDescription && this.engagementDescription.length > 0 ? 'Invalid engagement description' : 'Engagement description is required'
      } else {
        this.engagementIdState = (this.engagementId && this.engagementId > 0)
        this.nameState = null
        this.descriptionState = null
      }
      return this.productIdState !== false && this.engagementIdState !== false && this.nameState !== false && this.descriptionState !== false
    },
    clean () {
      this.sync = null
      this.autoProduct = null
      this.autoEngagement = null
      this.newEngagement = null
      this.productId = null
      this.engagementId = null
      this.engagementName = null
      this.engagementDescription = null
      this.productIdState = null
      this.engagementIdState = null
      this.nameState = null
      this.descriptionState = null
      this.$emit('clean')
    }
  }
}
</script>