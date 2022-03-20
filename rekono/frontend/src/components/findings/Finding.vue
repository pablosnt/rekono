<template>
  <b-col v-if="findings && findings.length > 0 && (types.length === 0 || types.includes(name.toLowerCase()))">
    <b-table ref="findingTable" select-mode="single" :selectable="details !== null" hover striped borderless head-variant="dark" selected-variant="danger" :fields="fields" :items="findings" :filter="findingId ? findingId.toString() : null" :filter-function="selectedFilter" @filtered="preventSelection = true" @row-selected="selectRow">
      <template #cell(data_type)="row">
        <b-badge variant="primary">{{ row.item.data_type }}</b-badge>
      </template>
      <template #cell(os_type)="row">
        <div v-for="type in osTypeByIcon" :key="type.value">
          <div v-if="row.item.os_type === type.value">
            <v-icon :fill="type.color" :name="type.icon" /><b-badge :variant="type.variant" class="ml-1">{{ row.item.os_type }}</b-badge>
          </div>
        </div>
      </template>
      <template #cell(port_status)="row">
        <div v-for="variant in portStatusByVariant" :key="variant.value">
          <div v-if="variant.value === row.item.port_status">
            <b-badge :variant="variant.variant">{{ row.item.port_status }}</b-badge>
          </div>
        </div>
      </template>
      <template #cell(severity)="row">
        <div v-for="s in severityByVariant" :key="s.value">
          <b-badge v-if="s.value == row.item.severity" :variant="s.variant">{{ row.item.severity.toUpperCase() }}</b-badge>
        </div>
      </template>
      <template #cell(cve)="row">
        <b-badge variant="primary">{{ row.item.cve }}</b-badge>
      </template>
      <template #row-details="row">
        <b-row>
          <b-col>
            <div v-for="detail in details" :key="detail.field">
              <div v-if="row.item[detail.field]">
                <div v-if="detail.type === 'text' && row.item[detail.field].length > 0" class="text-left">
                  <div v-if="detail.title">
                    <label class="text-muted">{{ detail.title }}</label><span class="ml-2">{{ row.item[detail.field] }}</span>
                  </div>
                  <div v-if="!detail.title">
                    <span>{{ row.item[detail.field] }}</span>
                  </div> 
                </div>
                <div v-if="detail.type === 'link' && row.item[detail.field].length > 0" class="text-left">
                  <b-link :href="row.item[detail.field]" target="_blank">{{ detail.title }}</b-link>
                </div>
                <div v-if="detail.type === 'badge' && detail.variant && row.item[detail.field].length > 0" class="text-left">
                  <div v-if="detail.title">
                    <label class="text-muted">{{ detail.title }}</label><b-badge class="ml-2" :variant="detail.variant">{{ row.item[detail.field] }}</b-badge>
                  </div>
                  <div v-if="!detail.title">
                    <b-badge :variant="detail.variant">{{ row.item[detail.field] }}</b-badge>
                  </div> 
                </div>
                <div v-if="detail.type === 'badge' && detail.variants && row.item[detail.field].length > 0" class="text-left">
                  <div v-for="variant in detail.variants" :key="variant.value">
                    <div v-if="variant.value === row.item[detail.field]">
                      <div v-if="detail.title">
                        <label class="text-muted">{{ detail.title }}</label><b-badge class="ml-2" :variant="variant.variant">{{ row.item[detail.field] }}</b-badge>
                      </div>
                      <div v-if="!detail.title">
                        <b-badge :variant="variant.variant">{{ row.item[detail.field] }}</b-badge>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-if="detail.type === 'boolean'" class="text-left">
                  <label class="text-muted">{{ detail.title }}</label><b-icon class="ml-2" v-if="row.item[detail.field]" icon="check-circle-fill" variant="success"/><b-icon class="ml-2" v-if="!row.item[detail.field]" icon="x-circle-fill" variant="danger"/>
                </div>
              </div>
            </div>
          </b-col>
          <b-col cols="2" v-if="auditor.includes($store.state.role)">
            <b-dropdown variant="outline" right>
              <template #button-content>
                <b-icon variant="dark" icon="three-dots-vertical"/>
              </template>
              <b-dropdown-item :disabled="row.item.is_active" @click="enableFinding(row.item)">
                <b-icon variant="success" icon="check-circle-fill"/> Enable
              </b-dropdown-item>
              <b-dropdown-item :disabled="!row.item.is_active" @click="selectFinding(row.item)" v-b-modal.disable-finding-modal>
                <b-icon variant="danger" icon="dash-circle-fill"/> Disable
              </b-dropdown-item>
              <b-dropdown-item :disabled="!row.item.is_active" @click="selectFinding(row.item)" v-b-modal.defect-dojo-modal>
                <b-img src="/static/defect-dojo-favicon.ico" width="20" height="20"/> Import in Defect-Dojo
              </b-dropdown-item>
              <b-dropdown-item v-if="name === 'osint' && (row.item.data_type === 'IP' || row.item.data_type === 'Domain')" :disabled="row.item.active"  @click="selectFinding(row.item)" v-b-modal.confirm-target>
                <b-icon variant="danger" icon="geo-fill"/> Create target
              </b-dropdown-item>
            </b-dropdown>
          </b-col>
        </b-row>
      </template>
    </b-table>
    <b-modal id="confirm-target" @ok="createTargetFromOSINT" title="New Target" ok-title="Create Target" header-bg-variant="dark" header-text-variant="light" ok-variant="dark" v-if="name === 'osint' && selectedFinding">
      <p>You will create the target <strong>{{ selectedFinding.target }}</strong>. Are you sure?</p>
    </b-modal>
    <deletion id="disable-finding-modal" title="Disable Finding" @deletion="disableFinding" @clean="cleanSelection" v-if="selectedFinding !== null">
      <span>selected finding</span>
    </deletion>
    <defect-dojo id="defect-dojo-modal" :path="name" :itemId="selectedFinding.id" :alreadyReported="selectedFinding.reported_to_defectdojo" @clean="cleanDDSelection" @confirm="cleanDDSelection" v-if="selectedFinding"/>
  </b-col>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import DefectDojo from '@/modals/DefectDojo'
export default {
  name: 'findingBase',
  mixins: [RekonoApi],
  props: {
    name: String,
    fields: Array,
    selectedFindingTypes: Array,
    findingId: Number,
    target: Number,
    task: Number,
    execution: Number,
    search: String,
    active: String,
    filter: Object,
    details: Array,
    reload: Boolean
  },
  computed: {
    filterChange () {
      return this.selectedFindingTypes.toString() + this.target + this.task + this.execution + this.search + this.active + JSON.stringify(this.filter) + this.reload
    },
    types () {
      let types = []
      this.selectedFindingTypes.forEach(item => types.push(item.toLowerCase()))
      return types
    }
  },
  data () {
    this.fetchData()
    return {
      findings: [],
      selectedFinding: null,
      preventSelection: false,
      defectDojo: process.env.VUE_APP_DEFECTDOJO_HOST
    }
  },
  components: {
    Deletion,
    DefectDojo
  },
  watch: {
    filterChange () {
      this.fetchData()
    }
  },
  methods: {
    selectedFilter (record) {
      return (!this.findingId || record.id === this.findingId)
    },
    getFilter () {
      let filter = {}
      if (this.execution) {
        filter.executions = this.execution
      } else if (this.task) {
        filter.executions__task = this.task
      } else if (this.target) {
        filter.executions__task__target = this.target
      } 
      if (this.search) {
        filter.search = this.search
      } else if (this.types && !this.types.includes(this.name.toLowerCase()) && this.filter) {
        filter = Object.assign({}, filter, this.filter)
      }
      if (this.active !== null) {
        filter.is_active = this.active.toString()
      }
      return filter
    },
    fetchData () {
      if (this.types && this.types.length > 0 && !this.types.includes(this.name.toLowerCase())) {
        return
      }
      if (this.target || this.task || this.execution) {
        this.getAllPages(`/api/${this.name.toLowerCase()}/?o=-creation`, this.getFilter()).then(results => this.findings = results)
      }
    },
    enableFinding (finding) {
      this.post(`/api/${this.name}/${finding.id}/enable/`, { }, 'Enable finding', 'Finding enabled successfully').then(() => this.fetchData())
    },
    disableFinding () {
      this.delete(`/api/${this.name}/${this.selectedFinding.id}/`, 'Disable finding', 'Finding disabled successfully').then(() => this.fetchData())
    },
    createTargetFromOSINT () {
      this.post(`/api/osint/${this.selectedFinding.id}/target/`, { }, this.selectedFinding.data, 'Target created successfully')
    },
    selectFinding (finding) {
      this.selectedFinding = finding
    },
    selectRow (items) {
      let row = (items && items.length > 0) ? items[0] : null
      if (row && this.findingId && !this.preventSelection) {
        this.$refs.findingTable.clearSelected()
      } else if (!this.findingId || !this.preventSelection) {
        if (row) {
          row._showDetails = true;
        } else {
          this.$refs.findingTable.items.forEach(r => r._showDetails = false)
        }
        this.$emit('finding-selected', { type: this.name, finding: row })
      }
      this.preventSelection = false
    },
    cleanDDSelection () {
      this.$bvModal.hide('defect-dojo-modal')
      this.cleanSelection()
    },
    cleanSelection () {
      this.selectedFinding = null
    }
  }
}
</script>
