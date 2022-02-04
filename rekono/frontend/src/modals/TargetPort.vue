<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="New Target Port" ok-title="Create Target Port" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="target_form">
      <b-form-group :invalid-feedback="invalidTargetPort">
        <b-form-input type="number" v-model="targetPort" placeholder="Target Port" :state="targetPortState" autofocus/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'targetPortModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    targetId: Number
  },
  data () {
    return {
      targetPort: null,
      targetPortState: null,
      invalidTargetPort: 'Target port is required'
    }
  },
  methods: {
    check () {
      const valid = this.$refs.target_form.checkValidity()
      this.targetPortState = (this.targetPort && this.targetPort > 0 && this.targetPort < 999999)
      this.invalidTargetPort = this.targetPort ? 'Invalid port value' : 'Target port is required'
      return valid && this.targetPortState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.post('/api/target-ports/', { target: this.targetId, port: this.targetPort }, this.targetPort, 'New target port created successfully')
          .then(() => { return Promise.resolve(true) })
          .catch(() => { return Promise.resolve(false) })
          .then(success => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    clean () {
      this.targetPort = null
      this.targetPortState = null
    }
  }
}
</script>
