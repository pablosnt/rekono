<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="New Target Port" ok-title="Create Target Port" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="target_form">
      <b-form-group invalid-feedback="Target is required">
        <b-form-input type="number" v-model="targetPort" placeholder="Target Port" :state="targetPortState" max-length="100" autofocus/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import Targets from '@/backend/targets'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
const TargetPortsApi = Targets.TargetPortsApi
export default {
  name: 'targetPortForm',
  mixins: [AlertMixin],
  props: ['id', 'targetId'],
  data () {
    return {
      targetPort: null,
      targetPortState: null
    }
  },
  methods: {
    check () {
      this.targetPortState = (this.targetPort && this.targetPort > 0)
      return this.targetPortState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.createTargetPort()
          .then(success => {
            this.$emit('confirm', { id: this.id, success: success, reload: true })
          })
      }
    },
    createTargetPort () {
      return TargetPortsApi.createTargetPort(this.targetId, this.targetPort)
        .then(() => {
          this.success(this.targetPort, 'New target port created successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.targetPort, 'Unexpected error in target port creation')
          return Promise.resolve(false)
        })
    },
    clean () {
      this.targetPort = null
      this.targetPortState = null
    }
  }
}
</script>
