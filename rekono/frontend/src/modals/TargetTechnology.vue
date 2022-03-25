<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" title="New Target Technology" ok-title="Create Target Technology" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="target_form">
      <b-form-group :invalid-feedback="invalidName">
        <b-form-input type="text" v-model="name" placeholder="Technology Name" :state="nameState" max-length="100" autofocus/>
      </b-form-group>
      <b-form-group :invalid-feedback="invalidVersion">
        <b-form-input type="text" v-model="version" placeholder="Technology Version" :state="versionState" max-length="100" autofocus/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'targetTechnologyModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    targetPortId: Number
  },
  data () {
    return {
      name: null,
      version: null,
      nameState: null,
      versionState: null,
      invalidName: 'Technology name is required',
      invalidVersion: 'Technology version is required'
    }
  },
  methods: {
    check () {
      const valid = this.$refs.target_form.checkValidity()
      if (!this.validateName(this.name)) {
        this.nameState = false
        this.invalidName = this.name && this.name.length > 0 ? 'Invalid technology name' : 'Technology name is required'
      }
      if (!this.validateName(this.version)) {
        this.versionState = false
        this.invalidVersion = this.version && this.version.length > 0 ? 'Invalid technology version' : 'Technology version is required'
      }
      return valid && this.nameState !== false && this.versionState !== false
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        this.post('/api/target-technologies/', { target_port: this.targetPortId, name: this.name, version: this.version }, this.name, 'New target technology created successfully')
          .then(() => { return Promise.resolve(true) })
          .catch(() => { return Promise.resolve(false) })
          .then(success => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    clean () {
      this.name = null
      this.version = null
      this.nameState = null
      this.versionState = null
    }
  }
}
</script>
