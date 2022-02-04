<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="New Target Endpoint" ok-title="Create Target Endpoint" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="target_form">
      <b-form-group :invalid-feedback="invalidTargetEndpoint">
        <b-form-input type="text" v-model="targetEndpoint" placeholder="Target Endpoint" :state="targetEndpointState" max-length="500" autofocus/>
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
      targetEndpoint: null,
      targetEndpointState: null,
      invalidTargetEndpoint: 'Target endpoint is required'
    }
  },
  methods: {
    check () {
      const valid = this.$refs.target_form.checkValidity()
      if (!this.targetEndpoint || this.targetEndpoint.length === 0 || !this.validateEndpoint(this.targetEndpoint)) {
        this.targetEndpointState = false
        this.invalidTargetEndpoint = this.targetEndpoint && this.targetEndpoint.length > 0 ? 'Invalid target endpoint' : 'Target endpoint is required'
      }
      return valid && this.targetEndpointState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.post('/api/target-endpoints/', { target_port: this.targetPortId, endpoint: this.targetEndpoint }, this.targetEndpoint, 'New target endpoint created successfully')
          .then(() => { return Promise.resolve(true) })
          .catch(() => { return Promise.resolve(false) })
          .then(success => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    clean () {
      this.targetEndpoint = null
      this.targetEndpointState = null
    }
  }
}
</script>
