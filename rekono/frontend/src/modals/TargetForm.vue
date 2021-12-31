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
import Targets from '@/backend/targets'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
const TargetsApi = Targets.TargetsApi
export default {
  name: 'targetForm',
  mixins: [AlertMixin],
  props: ['id', 'projectId'],
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
        this.createTarget()
          .then(success => {
            this.$emit('confirm', { id: this.id, success: success, reload: true })
          })
      }
    },
    createTarget () {
      return TargetsApi.createTarget(this.projectId, this.target)
        .then(() => {
          this.success(this.target, 'New target created successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.target, 'Unexpected error in target creation')
          return Promise.resolve(false)
        })
    },
    clean () {
      this.target = null
      this.targetState = null
    }
  }
}
</script>
