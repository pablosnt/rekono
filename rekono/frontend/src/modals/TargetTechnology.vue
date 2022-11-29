<template>
  <b-row>
    <b-col cols="10">
      <b-form>
        <b-row>
          <b-col cols="6">
            <b-form-group :invalid-feedback="invalidTech">
              <b-form-input type="text" v-model="newTech" placeholder="Technology Name" :state="techState" autofocus/>
            </b-form-group>
          </b-col>
          <b-col cols="6">
            <b-form-group :invalid-feedback="invalidVersion">
              <b-form-input type="text" v-model="newVersion" placeholder="Technology Version" :state="versionState" autofocus/>
            </b-form-group>
          </b-col>
        </b-row>
      </b-form>
    </b-col>
    <b-col cols="2">
      <b-button variant="outline" @click="create" v-b-tooltip.hover title="Create">
        <p class="h3"><b-icon variant="success" icon="plus-square-fill"/></p>
      </b-button>
    </b-col>
  </b-row>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi';
export default {
  name: 'targetTechnology',
  mixins: [RekonoApi],
  props: {
    targetPortId: Number,
  },
  data () {
    return {
      newTech: null,
      newVersion: null,
      invalidTech: 'Technology name is required',
      invalidVersion: 'Technology version is required',
      techState: null,
      versionState: null
    }
  },
  methods: {
    check () {
      this.techState = null
      this.versionState = null
      if (!this.validateName(this.newTech)) {
        this.techState = false
        this.invalidName = this.newTech && this.newTech.length > 0 ? 'Invalid technology name' : 'Technology name is required'
      }
      if (!this.validateName(this.newVersion)) {
        this.versionState = false
        this.invalidVersion = this.newVersion && this.newVersion.length > 0 ? 'Invalid technology version' : 'Technology version is required'
      }
      return this.techState !== false && this.versionState !== false
    },
    create () {
      if (this.check()) {
        this.post(
          '/api/target-technologies/',
          { target_port: this.targetPortId, name: this.newTech, version: this.newVersion },
          this.newTech, `New target ${this.name} created successfully`
        )
          .then(() => this.$emit('update'))
        this.clean()
      }
    },
    clean () {
      this.newTech = null
      this.newVersion = null
      this.invalidTech = 'Technology name is required'
      this.invalidVersion = 'Technology version is required'
      this.techState = null
      this.versionState = null
    }
  }
}
</script>