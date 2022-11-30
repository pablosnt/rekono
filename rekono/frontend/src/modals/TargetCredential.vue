<template>
  <b-row>
    <b-col cols="1">
      <b-input-group-append v-b-tooltip.hover title="The following tools accept credentials to perform authenticated analysis: Dirsearch (all authentication types), SMBMap (basic authentication), JoomScan (cookie authentication) and OWASP ZAP">
        <b-button variant="outline">
          <b-icon icon="info-circle-fill" variant="info"/>
        </b-button>
      </b-input-group-append>
    </b-col>
    <b-col cols="9">
      <b-form>
        <b-row>
          <b-col cols="3">
            <b-form-select v-model="newType" :options="credentialTypes">Type</b-form-select>
          </b-col>
          <b-col cols="4">
            <b-form-group :invalid-feedback="invalidName">
              <b-form-input type="text" v-model="newName" :placeholder="newType === 'Basic' ? 'Username' : newType === 'Cookie' ? 'Cookie name' : 'Credential name'" :state="nameState" autofocus/>
            </b-form-group>
          </b-col>
          <b-col cols="5">
            <b-form-group :invalid-feedback="invalidCredential">
              <b-form-input type="password" v-model="newCredential" :placeholder="newType === 'Basic' ? 'Password' : newType === 'Cookie' ? 'Cookie value' : 'Credential value'" :state="credentialState" autofocus/>
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
      newType: 'Basic',
      newName: null,
      newCredential: null,
      invalidName: 'Credential name is required',
      invalidCredential: 'Credential value is required',
      nameState: null,
      credentialState: null
    }
  },
  methods: {
    check () {
      this.nameState = null
      this.credentialState = null
      if (!this.validateName(this.newName)) {
        this.techState = false
        this.invalidName = this.newName && this.newName.length > 0 ? 'Invalid credential name' : 'Credential name is required'
      }
      if (!this.validateCredential(this.newCredential)) {
        this.credentialState = false
        this.invalidCredential = this.newCredential && this.newCredential.length > 0 ? 'Invalid credential value' : 'Credential value is required'
      }
      return this.nameState !== false && this.credentialState !== false
    },
    create () {
      if (this.check()) {
        this.post(
          '/api/target-credentials/',
          { target_port: this.targetPortId, name: this.newName, credential: this.newCredential, type: this.newType },
          this.newName, 'New target credential created successfully'
        )
          .then(() => this.$emit('update'))
        this.clean()
      }
    },
    clean () {
      this.newName = null
      this.newCredential = null
      this.invalidName = 'Credential name is required'
      this.invalidCredential = 'Credential value is required'
      this.nameState = null
      this.credentialState = null
    }
  }
}
</script>