<template>
  <div>
    <b-row>
      <b-col cols="10">
        <b-form  v-if="name === 'vulnerability'">
          <b-form-group :invalid-feedback="invalidCve">
            <b-form-input type="text" v-model="newCve" placeholder="CVE" :state="cveState" autofocus/>
          </b-form-group>
        </b-form>
        <b-form  v-if="name === 'technology'">
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
    <b-table stripped head-variant="light" :fields="tableFields" :items="data" v-if="data.length > 0">
      <template #cell(actions)="row">
        <b-button variant="outline" @click="selectItem(row.item)" v-b-tooltip.hover title="Delete" v-b-modal="'delete-' + name + '-modal'">
          <b-icon variant="danger" icon="trash-fill"/>
        </b-button>
      </template>
    </b-table>
    <deletion :id="'delete-' + name + '-modal'" :title="'Delete ' + name.charAt(0).toUpperCase() + name.slice(1)" @deletion="deleteItem" @clean="cleanSelection" v-if="selectedItem !== null">
      <span><strong>{{ selectedItem[field] }}</strong> {{ name.toLowerCase() }}</span>
    </deletion>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" :name="endpoint" @pagination="pagination"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import Pagination from '@/common/Pagination'
export default {
  name: 'targetPortDetails',
  mixins: [RekonoApi],
  props: {
    targetPortId: Number,
    endpoint: String,
    name: String,
    field: String,
    fields: Array
  },
  computed: {
    tableFields () {
      let all_fields = this.fields
      all_fields.push({ key: 'actions' })
      return all_fields
    }
  },
  components: {
    Deletion,
    Pagination
  },
  data () {
    this.fetchData()
    return {
      limit: 10,
      limits: [10, 25, 50, 100],
      data: [],
      selectedItem: null,
      newEndpoint: null,
      invalidEndpoint: 'Endpoint is required',
      endpointState: null,
      newCve: null,
      invalidCve: 'CVE is required',
      cveState: null,
      newTech: null,
      newVersion: null,
      invalidTech: 'Technology name is required',
      invalidVersion: 'Technology version is required',
      techState: null,
      versionState: null
    }
  },
  methods: {
    fetchData () {
      return this.getOnePage(`/api/target-${this.endpoint}/?o=${this.field}`, { target_port: this.targetPortId })
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    check () {
      this.endpointState = null
      this.cveState = null
      this.techState = null
      this.versionState = null
      if (this.name === 'vulnerability' && !this.validateCve(this.newCve)) {
        this.cveState = false
        this.invalidCve = this.newCve && this.newCve.length > 0 ? 'Invalid CVE' : 'CVE is required'
        return false
      } else if (this.name === 'technology') {
        if (!this.validateName(this.newTech)) {
          this.techState = false
          this.invalidName = this.newTech && this.newTech.length > 0 ? 'Invalid technology name' : 'Technology name is required'
        }
        if (!this.validateName(this.newVersion)) {
          this.versionState = false
          this.invalidVersion = this.newVersion && this.newVersion.length > 0 ? 'Invalid technology version' : 'Technology version is required'
        }
        return this.techState !== false && this.versionState !== false
      }
      return true
    },
    create () {
      if (this.check()) {
        let creationData = {
          target_port: this.targetPortId
        }
        if (this.name === 'vulnerability') {
          creationData['cve'] = this.newCve
        } else if (this.name === 'technology') {
          creationData['name'] = this.newTech
          creationData['version'] = this.newVersion
        }
        this.post(`/api/target-${this.endpoint}/`, creationData, creationData[this.field], `New target ${this.name} created successfully`)
          .then(() => this.fetchData())
        this.clean()
      }
    },
    deleteItem () {
      this.delete(`/api/target-${this.endpoint}/${this.selectedItem.id}/`).then(() => this.fetchData())
    },
    selectItem (item) {
      this.selectedItem = item
    },
    clean () {
      this.newEndpoint = null
      this.invalidEndpoint = 'Endpoint is required'
      this.endpointState = null
      this.newCve = null
      this.invalidCve = 'CVE is required'
      this.cveState = null
      this.newTech = null
      this.newVersion = null
      this.invalidTech = 'Technology name is required'
      this.invalidVersion = 'Technology version is required'
      this.techState = null
      this.versionState = null
    },
    cleanSelection () {
      this.selectedItem = null
    }
  }
}
</script>