<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="New Target Endpoint" ok-title="Create Target Endpoint" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="target_form">
      <b-form-group :invalid-feedback="invalidEndpoint">
        <b-form-input type="text" v-model="endpoint" placeholder="Endpoint" :state="endpointState" max-length="500" autofocus/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'targetEndpointModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    targetPortId: Number
  },
  data () {
    return {
      endpoint: null,
      endpointState: null,
      invalidEndpoint: 'Endpoint is required'
    }
  },
  methods: {
    check () {
      const valid = this.$refs.target_form.checkValidity()
      if (!this.validatePath(this.endpoint)) {
        this.endpointState = false
        this.invalidEndpoint = this.endpoint && this.endpoint.length > 0 ? 'Invalid endpoint' : 'Endpoint is required'
      }
      return valid && this.endpointState !== false
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.post('/api/target-endpoints/', { target_port: this.targetPortId, endpoint: this.endpoint }, this.endpoint, 'New target endpoint created successfully')
          .then(() => { return Promise.resolve(true) })
          .catch(() => { return Promise.resolve(false) })
          .then(success => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    clean () {
      this.endpoint = null
      this.endpointState = null
    }
  }
}
</script>
