<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="New Target" ok-title="Create Target" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="target_form">
      <b-form-group invalid-feedback="Target is required">
        <b-form-input type="text" v-model="target" placeholder="Target" :state="targetState" max-length="100" autofocus/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'targetModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    projectId: [Number, String]
  },
  data () {
    return {
      target: null,
      targetState: null
    }
  },
  methods: {
    check () {
      this.targetState = (this.target && this.target.length > 0)
      return this.targetState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.post('/api/targets/', { project: this.projectId, target: this.target }, this.target, 'New target created successfully')
          .then(() => { return Promise.resolve(true) })
          .catch(() => { return Promise.resolve(false) })
          .then(success => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    clean () {
      this.target = null
      this.targetState = null
    }
  }
}
</script>
