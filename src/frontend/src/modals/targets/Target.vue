<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="New Targets" ok-title="Create Targets" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="target_form">
      <b-form-group invalid-feedback="Targets are required">
        <b-form-tags v-model="targets" placeholder="New target" :state="targetState" separator=" ,;<>_" tag-variant="danger" remove-on-delete add-on-change/>
      </b-form-group>
    </b-form>
    <b-progress v-if="processed > 0 && targets.length > 1" :value="processed" :max="targets.length" variant="danger" show-value/>
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
      targets: [],
      targetState: null,
      processed: 0
    }
  },
  methods: {
    check () {
      this.targetState = this.targets.length > 0
      return this.targetState
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        for (let index in this.targets) {
          this.post('/api/targets/', { project: this.projectId, target: this.targets[index] }, this.targets[index], 'New target created successfully')
            .catch(() => { return Promise.resolve(false) })
            .then(() => {
              this.processed += 1
              if (this.processed === this.targets.length) {
                this.$emit('confirm', { id: this.id, success: true, reload: true })
              }
            })
        }
      }
    },
    clean () {
      this.targets = []
      this.targetState = null
      this.processed = 0
    }
  }
}
</script>
