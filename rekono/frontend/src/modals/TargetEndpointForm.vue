<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="New Target Endpoint" ok-title="Create Target Endpoint" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="target_form">
      <b-form-group invalid-feedback="Target is required">
        <b-form-input type="text" v-model="targetEndpoint" placeholder="Target Endpoint" :state="targetEndpointState" max-length="500" autofocus/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import Targets from '@/backend/targets'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
const TargetEndpointsApi = Targets.TargetEndpointsApi
export default {
  name: 'targetEndpointForm',
  mixins: [AlertMixin],
  props: ['id', 'targetPortId'],
  data () {
    return {
      targetEndpoint: null,
      targetEndpointState: null
    }
  },
  methods: {
    check () {
      this.targetEndpointState = (this.targetEndpoint && this.targetEndpoint.length > 0)
      return this.targetEndpointState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.createTargetEndpoint()
          .then(success => {
            this.$emit('confirm', { id: this.id, success: success, reload: true })
          })
      }
    },
    createTargetEndpoint () {
      return TargetEndpointsApi.createTargetEndpoint(this.targetPortId, this.targetEndpoint)
        .then(() => {
          this.success(this.targetEndpoint, 'New target endpoint created successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.targetEndpoint, 'Unexpected error in target endpoint creation')
          return Promise.resolve(false)
        })
    },
    clean () {
      this.targetEndpoint = null
      this.targetEndpointState = null
    }
  }
}
</script>
