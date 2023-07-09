<template>
  <div>
    <b-row>
      <b-col cols="10">
        <b-form>
          <b-row>
            <b-col cols="2">
              <b-input-group-append v-b-tooltip.hover title="Ports can be created with and without authentication to perform specific analysis.The following tools accept credentials to perform authenticated analysis: Dirsearch, Gobuster, Nuclei, OWASP ZAP (all authentication types), SMBMap (basic authentication), JoomScan (cookie authentication) and Nikto (cookie and basic authentication)">
                <b-button variant="outline">
                  <b-icon icon="info-circle-fill" variant="info"/>
                </b-button>
              </b-input-group-append>
            </b-col>
            <b-col cols="5">
              <b-form-input type="number" v-model="port" placeholder="Target Port" :state="portState" autofocus/>
            </b-col>
            <b-col cols="5">
              <b-form-select v-model="type" :options="authenticationTypes">Authentication Type</b-form-select>
            </b-col>
          </b-row>
          <b-row v-if="type !== 'None'" class="mt-3">
            <b-col>
              <b-form-group :invalid-feedback="invalidName">
                <b-form-input type="text" v-model="name" :placeholder="type === 'Basic' ? 'Username' : type === 'Cookie' ? 'Cookie name' : 'Credential name'" :state="nameState" autofocus/>
              </b-form-group>
            </b-col>
            <b-col>
              <b-form-group :invalid-feedback="invalidCredential">
                <b-form-input type="password" v-model="credential" :placeholder="type === 'Basic' ? 'Password' : type === 'Cookie' ? 'Cookie value' : 'Credential value'" :state="credentialState" autofocus/>
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
      <template #cell(authentication.type)="row">
        <b-form-select value="None" :options="authenticationTypes" @input="selectedItemToAddAuth = row.item" @change="selectTypeToAddAuth" v-if="!row.item.authentication"/>
        <p v-if="row.item.authentication">{{ row.item.authentication.type }}</p>
      </template>
      <template #cell(authentication.name)="row">
        <b-form-input type="text" v-model="nameToAddAuth" :placeholder="typeToAddAuth === 'Basic' ? 'Username' : typeToAddAuth === 'Cookie' ? 'Cookie name' : 'Credential name'" v-if="!row.item.authentication && selectedItemToAddAuth && selectedItemToAddAuth.id === row.item.id"/>
        <p v-if="!row.item.authentication && (!selectedItemToAddAuth || selectedItemToAddAuth.id !== row.item.id)"></p>
        <p v-if="row.item.authentication">{{ row.item.authentication.name }}</p>
      </template>
      <template #cell(authentication.credential)="row">
        <b-form-input type="password" v-model="credentialToAddAuth" :placeholder="typeToAddAuth === 'Basic' ? 'Password' : typeToAddAuth === 'Cookie' ? 'Cookie value' : 'Credential value'" v-if="!row.item.authentication && selectedItemToAddAuth && selectedItemToAddAuth.id === row.item.id"/>
        <p v-if="!row.item.authentication && (!selectedItemToAddAuth || selectedItemToAddAuth.id !== row.item.id)"></p>
        <p v-if="row.item.authentication">{{ row.item.authentication.credential }}</p>
      </template>
      <template #cell(actions)="row">
        <b-button variant="outline" @click="createAuthentication" v-b-tooltip.hover title="Add Authentication" :disabled="!checkAuthentication(typeToAddAuth, nameToAddAuth, credentialToAddAuth, false)" v-if="selectedItemToAddAuth && selectedItemToAddAuth.id === row.item.id">
          <b-icon variant="success" icon="plus-square-fill"/>
        </b-button>
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
        { key: 'authentication.type', label: 'Auth Type', sortable: true },
        { key: 'authentication.name', label: 'Name', sortable: true },
        { key: 'authentication.credential', label: 'Credential', sortable: true }
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
      port: null,
      type: 'None',
      name: null,
      credential: null,
      selectedItemToAddAuth: null,
      typeToAddAuth: 'None',
      nameToAddAuth: null,
      credentialToAddAuth: null,      
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
      return this.getOnePage('/api/target-ports/', { o: 'port', target: this.targetId })
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    checkPort () {
      this.portState = null
      if (!this.port || this.port < 0 || this.port > 999999) {
        this.portState = false
        this.invalidPort = this.port ? 'Invalid port value' : 'Target port is required'
      }
      return this.portState !== false
    },
    checkAuthentication (type = this.type, name = this.name, credential = this.credential, changeState = true) {
      if (changeState) {
        this.nameState = null
        this.credentialState = null
      }
      if (type !== 'None') {
        if (!this.validateName(name)) {
          if (changeState) {
            this.techState = false
            this.invalidName = name && name.length > 0 ? 'Invalid credential name' : 'Credential name is required'
          } else {
            return false
          }
        }
        if (!this.validateCredential(credential)) {
          if (changeState) {
            this.credentialState = false
            this.invalidCredential = credential && credential.length > 0 ? 'Invalid credential value' : 'Credential value is required'
          } else {
            return false
          }
        }
      }
      return changeState ? this.nameState !== false && this.credentialState !== false : true
    },
    create () {
      if (this.checkPort() && this.checkAuthentication()) {
        this.post('/api/target-ports/', { target: this.targetId, port: this.port }, this.port, 'New target port created successfully')
          .then(data => {
            if (this.type !== 'None') {
              this.post(
                '/api/authentications/',
                { target_port: data.id, name: this.name, credential: this.credential, type: this.type},
                this.name, 'New authentication created successfully'
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
      else {
        this.clean()
      }
    },
    createAuthentication () {
      if (this.selectedItemToAddAuth && this.checkAuthentication(this.typeToAddAuth, this.nameToAddAuth, this.credentialToAddAuth, false)) {
        this.post(
          '/api/authentications/',
          { target_port: this.selectedItemToAddAuth.id, name: this.nameToAddAuth, credential: this.credentialToAddAuth, type: this.typeToAddAuth},
          this.nameToAddAuth, 'New authentication created successfully'
        )
          .then(() => this.fetchData())
        this.selectedItemToAddAuth = null
        this.typeToAddAuth = null
        this.nameToAddAuth = null
        this.credentialToAddAuth = null
      }
    },
    deletePort () {
      this.delete(`/api/target-ports/${this.selectedItem.id}/`, this.selectedItem.port, 'Port deleted successfully').then(() => this.fetchData())
    },
    deleteAuthentication () {
      this.delete(`/api/authentications/${this.selectedItem.id}/`, this.selectedItem.name, 'Authentication deleted successfully').then(() => this.fetchData())
    },
    selectTypeToAddAuth (type) {
      if (type === 'None') {
        this.selectedItemToAddAuth = null
      } else {
        this.typeToAddAuth = type
      }
    },
    clean () {
      this.selectedItem = null
      this.port = null
      this.type = 'None'
      this.name = null
      this.credential = null
      this.selectedItemToAddAuth = null
      this.typeToAddAuth = null
      this.nameToAddAuth = null
      this.credentialToAddAuth = null
      this.portState = null
      this.nameState = null
      this.credentialState = null
    }
  }
}
</script>