<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="New Target Port" ok-title="Create Target Port" header-bg-variant="dark" header-text-variant="light" ok-variant="dark" size="sm">
    <b-form-group :invalid-feedback="invalidPort">
      <b-form-input type="number" v-model="port" placeholder="Target Port" :state="portState" autofocus/>
    </b-form-group>
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
      port: null,
      portState: null,
      invalidPort: 'Target port is required'
    }
  },
  methods: {
    check () {
      this.portState = (this.port && this.port > 0 && this.port < 999999)
      this.invalidPort = this.port ? 'Invalid port value' : 'Target port is required'
      return this.portState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.post('/api/target-ports/', { target: this.targetId, port: this.port }, this.port, 'New target port created successfully')
          .then(() => { return Promise.resolve(true) })
          .catch(() => { return Promise.resolve(false) })
          .then(success => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    clean () {
      this.port = null
      this.portState = null
    }
  }
}
</script>