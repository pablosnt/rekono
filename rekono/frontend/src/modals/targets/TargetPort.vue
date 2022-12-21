<template>
  <div>
    <b-row>
      <b-col cols="10">
        <b-form>
          <b-row>
            <b-col cols="2">
              <b-input-group-append v-b-tooltip.hover title="Ports can be created with and without authentication to perform specific analysis.The following tools accept credentials to perform authenticated analysis: Dirsearch (all authentication types), SMBMap (basic authentication), JoomScan (cookie authentication), Nikto (cookie and basic authentication) and OWASP ZAP (all authentication types)">
                <b-button variant="outline">
                  <b-icon icon="info-circle-fill" variant="info"/>
                </b-button>
              </b-input-group-append>
            </b-col>
            <b-col cols="5">
              <b-form-input type="number" v-model="newPort" placeholder="Target Port" :state="portState" autofocus/>
            </b-col>
            <b-col cols="5">
              <b-form-select v-model="newType" :options="authenticationTypes">Authentication Type</b-form-select>
            </b-col>
          </b-row>
          <b-row v-if="newType !== 'None'" class="mt-3">
            <b-col>
              <b-form-group :invalid-feedback="invalidName">
                <b-form-input type="text" v-model="newName" :placeholder="newType === 'Basic' ? 'Username' : newType === 'Cookie' ? 'Cookie name' : 'Credential name'" :state="nameState" autofocus/>
              </b-form-group>
            </b-col>
            <b-col>
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
    <b-table stripped head-variant="light" :fields="fields" :items="data" v-if="data.length > 0">
      <template #cell(actions)="row">
        <b-dropdown variant="outline" right v-b-tooltip.hover title="Delete" v-if="row.item.authentication">
          <template #button-content>
            <b-icon variant="danger" icon="trash-fill"/>
          </template>
          <b-dropdown-item @click="selectedItem = row.item" v-b-modal.delete-port-modal>Delete port</b-dropdown-item>
          <b-dropdown-item @click="selectedItem = row.item.authentication" v-b-modal.delete-auth-modal>Delete authentication</b-dropdown-item>
        </b-dropdown>
        <b-button variant="outline" right v-b-tooltip.hover title="Delete" @click="selectedItem = row.item" v-b-modal.delete-port-modal v-if="!row.item.authentication">
          <b-icon variant="danger" icon="trash-fill"/>
        </b-button>
      </template>
    </b-table>
    <deletion id="delete-port-modal" title="Delete Port" @deletion="deletePort" @clean="selectedItem = null" v-if="selectedItem !== null">
      <span><strong>{{ selectedItem['port'] }}</strong> port</span>
    </deletion>
    <deletion id="delete-auth-modal" title="Delete Authentication" @deletion="deleteAuthentication" @clean="selectedItem = null" v-if="selectedItem !== null">
      <span><strong>{{ selectedItem['name'] }}</strong> authentication</span>
    </deletion>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="ports" @pagination="pagination"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi';
import Deletion from '@/common/Deletion';
import Pagination from '@/common/Pagination';
export default {
  name: 'targetPortModal',
  mixins: [RekonoApi],
  props: {
    targetId: Number,
  },
  computed: {
    fields () {
      let fields = [
        { key: 'port', sortable: true },
        { key: 'authentication.name', label: 'Authentication', sortable: true },
        { key: 'authentication.credential', label: 'Credential', sortable: true },
        { key: 'authentication.type', label: 'Authentication Type', sortable: true }
      ]
      if (this.auditor.includes(this.$store.state.role)) {
        fields.push({ key: 'actions', sortable: false })
      }
      return fields
    }
  },
  data () {
    this.fetchData()
    return {
      limit: 10,
      limits: [10, 25, 50, 100],
      data: [],
      selectedItem: null,
      newPort: null,
      newType: 'None',
      newName: null,
      newCredential: null,
      invalidPort: 'Target port is required',
      invalidName: 'Credential name is required',
      invalidCredential: 'Credential value is required',
      portState: null,
      nameState: null,
      credentialState: null
    }
  },
  components: {
    Deletion,
    Pagination
  },
  methods: {
    fetchData () {
      return this.getOnePage('/api/target-ports/?o=port', { target: this.targetId })
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    check () {
      this.portState = null
      this.nameState = null
      this.credentialState = null
      if (!this.newPort || this.newPort < 0 || this.newPort > 999999) {
        this.portState = false
        this.invalidPort = this.newPort ? 'Invalid port value' : 'Target port is required'
      }
      if (this.newType !== 'None') {
        if (!this.validateName(this.newName)) {
          this.techState = false
          this.invalidName = this.newName && this.newName.length > 0 ? 'Invalid credential name' : 'Credential name is required'
        }
        if (!this.validateCredential(this.newCredential)) {
          this.credentialState = false
          this.invalidCredential = this.newCredential && this.newCredential.length > 0 ? 'Invalid credential value' : 'Credential value is required'
        }
      }
      return this.portState !== false && this.nameState !== false && this.credentialState !== false
    },
    create () {
      if (this.check()) {
        this.post('/api/target-ports/', { target: this.targetId, port: this.newPort }, this.newPort, 'New target port created successfully')
          .then(data => {
            if (this.newType !== 'None') {
              this.post(
                '/api/authentications/',
                { target_port: data.id, name: this.newName, credential: this.newCredential, type: this.newType},
                this.newName, 'New authentication created successfully'
              )
                .then(() => this.fetchData())
                .catch(() => this.fetchData())
            } else {
              this.fetchData()
            }
            this.clean()
          })
        .catch(() => this.clean())
      }
    },
    deletePort () {
      this.delete(`/api/target-ports/${this.selectedItem.id}/`, this.selectedItem.port, 'Port deleted successfully').then(() => this.fetchData())
    },
    deleteAuthentication () {
      this.delete(`/api/authentications/${this.selectedItem.id}/`, this.selectedItem.name, 'Authentication deleted successfully').then(() => this.fetchData())
    },
    clean () {
      this.selectedItem = null
      this.newPort = null
      this.newType = 'None'
      this.newName = null
      this.newCredential = null
      this.portState = null
      this.nameState = null
      this.credentialState = null
    }
  }
}
</script>