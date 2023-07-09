<template>
  <div>
    <b-row>
      <b-col cols="1">
        <b-input-group-append v-b-tooltip.hover title="You can provide technologies to search related exploits using SearchSploit">
          <b-button variant="outline">
            <b-icon icon="info-circle-fill" variant="info"/>
          </b-button>
        </b-input-group-append>
      </b-col>
      <b-col cols="9">
        <b-form>
          <b-row>
            <b-col cols="6">
              <b-form-group :invalid-feedback="invalidName">
                <b-form-input type="text" v-model="name" placeholder="Technology Name" :state="nameState" autofocus/>
              </b-form-group>
            </b-col>
            <b-col cols="6">
              <b-form-group :invalid-feedback="invalidVersion">
                <b-form-input type="text" v-model="version" placeholder="Technology Version" :state="versionState" autofocus/>
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
        <b-button variant="outline" @click="selectedItem = row.item" v-b-tooltip.hover title="Delete" v-b-modal="'delete-technology-modal'">
          <b-icon variant="danger" icon="trash-fill"/>
        </b-button>
      </template>
    </b-table>
    <deletion id="delete-technology-modal" title="Delete Technology" @deletion="deleteTechnology" @clean="selectedItem = null" v-if="selectedItem !== null">
      <span><strong>{{ selectedItem['name'] }}</strong> technology</span>
    </deletion>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="technologies" @pagination="pagination"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi';
import Deletion from '@/common/Deletion';
import Pagination from '@/common/Pagination';
export default {
  name: 'technologyModal',
  mixins: [RekonoApi],
  props: {
    targetId: Number,
  },
  computed: {
    fields () {
      let fields = [
        { key: 'name', label: 'Technology', sortable: true },
        { key: 'version', sortable: true }
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
      name: null,
      version: null,
      invalidName: 'Technology name is required',
      invalidVersion: 'Technology version is required',
      nameState: null,
      versionState: null
    }
  },
  components: {
    Deletion,
    Pagination
  },
  methods: {
    fetchData () {
      return this.getOnePage('/api/parameters/technologies/', { o: 'name', target: this.targetId })
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    check () {
      this.nameState = null
      this.versionState = null
      if (!this.validateName(this.name)) {
        this.nameState = false
        this.invalidName = this.name && this.name.length > 0 ? 'Invalid technology name' : 'Technology name is required'
      }
      if (!this.validateName(this.version)) {
        this.versionState = false
        this.invalidVersion = this.version && this.version.length > 0 ? 'Invalid technology version' : 'Technology version is required'
      }
      return this.nameState !== false && this.versionState !== false
    },
    create () {
      if (this.check()) {
        this.post(
          '/api/parameters/technologies/',
          { target: this.targetId, name: this.name, version: this.version },
          this.name, 'New target technology created successfully'
        )
          .then(() => this.fetchData())
        this.clean()
      }
    },
    deleteTechnology () {
      this.delete(`/api/parameters/technologies/${this.selectedItem.id}/`).then(() => this.fetchData())
    },
    clean () {
      this.selectedItem = null
      this.name = null
      this.version = null
      this.invalidName = 'Technology name is required'
      this.invalidVersion = 'Technology version is required'
      this.nameState = null
      this.versionState = null
    }
  }
}
</script>