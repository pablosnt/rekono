<template>
  <b-col v-if="findings && findings.length > 0 && (selectedFindingTypes.length === 0 || selectedFindingTypes.includes(name.toLowerCase()))">
    <b-table select-mode="single" :selectable="details !== null" hover striped borderless head-variant="dark" :fields="fields" :items="findings" @row-clicked="displayRowDetails" @row-selected="selectRow">
      <template #cell(data_type)="row">
        <b-badge variant="primary">{{ row.item.data_type }}</b-badge>
      </template>
      <template #cell(os_type)="row">
        <div class="d-inline">
          <b-icon variant="warning" icon="terminal-fill" v-if="row.item.os_type === 'Linux'"/>
          <b-img src="/static/brands/windows.svg"  v-if="row.item.os_type === 'Windows'"/>
          <b-img src="/static/brands/apple.svg"  v-if="row.item.os_type === 'MacOS'"/>
          <b-img src="/static/brands/apple.svg"  v-if="row.item.os_type === 'iOS'"/>
          <b-icon variant="success" icon="phone-fill" v-if="row.item.os_type === 'Android'"/>
          <b-icon variant="warning" icon="sun" v-if="row.item.os_type === 'Solaris'"/>
          <b-icon variant="danger" icon="terminal-fill" v-if="row.item.os_type === 'FreeBSD'"/>
          <b-icon variant="dark" icon="terminal-fill" v-if="row.item.os_type === 'Other'"/>
          <span class="ml-1">{{ row.item.os_type }}</span>
        </div>
      </template>
      <template #cell(severity)="row">
        <div v-for="s in severities" :key="s.value">
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
              <div v-if="row.item[detail.field] !== null">
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
          <b-col cols="2">
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
              <!-- TODO -->
              <!-- <b-dropdown-item v-if="defectDojo" :disabled="row.item.active && row.item.reported_to_defectdojo" @click="selectFinding(row.item)" v-b-modal.confirm-dojo-import>
                <b-img src="/static/brands/defect-dojo-favicon.ico" width="30" height="30"/> Import in Defect-Dojo
              </b-dropdown-item> -->
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
    <Deletion id="disable-finding-modal"
      title="Disable Finding"
      @deletion="disableFinding"
      @clean="cleanSelection"
      v-if="selectedFinding !== null">
      <span>selected finding</span>
    </Deletion>
  </b-col>
</template>

<script>
import FindingsApi from '@/backend/findings'
import { severityByVariant } from '@/backend/constants'
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import Deletion from '@/common/Deletion.vue'
export default {
  name: 'findingBase',
  mixins: [AlertMixin],
  props: ['name', 'fields', 'findingTypes', 'target', 'task', 'execution', 'search', 'active', 'selection', 'details'],
  computed: {
    filterChange () {
      return this.findingTypes.toString() + this.target + this.task + this.execution + this.search + this.active + JSON.stringify(this.selection)
    },
    selectedFindingTypes () {
      let selection = []
      for (let f in this.findingTypes) {
        if (this.findingTypes[f]) {
          selection.push(this.findingTypes[f].toLowerCase())
        }
      }
      return selection
    }
  },
  data () {
    return {
      findings: [],
      selectedFinding: null,
      severities: severityByVariant,
      defectDojo: process.env.VUE_APP_DEFECTDOJO_HOST
    }
  },
  components: {
    Deletion
  },
  watch: {
    filterChange () {
      this.fetchData()
    }
  },
  methods: {
    getFilter () {
      let filter = {}
      if (this.execution) {
        filter.execution = this.execution
      } else if (this.task) {
        filter.execution__task = this.task
      } else if (this.target) {
        filter.execution__task__target = this.target
      } 
      if (this.search) {
        filter.search = this.search
      } else if (!this.selectedFindingTypes.includes(this.name.toLowerCase()) && this.selection) {
        filter = Object.assign({}, filter, this.selection)
      }
      if (this.active !== null) {
        filter.is_active = this.active.toString()
      }
      return filter
    },
    fetchData () {
      if ((this.task || this.target) && (this.selectedFindingTypes.length === 0 || this.selectedFindingTypes.includes(this.name.toLowerCase()))) {
        FindingsApi.getAllFindings(this.name.toLowerCase(), this.getFilter())
          .then(results => {
            this.findings = results
          })
      }
    },
    enableFinding (finding) {
      FindingsApi.enableFinding(this.name, finding.id)
        .then(() => {
          this.success('Enable finding', 'Finding enabled successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger('Enable finding', 'Unexpected error in finding enabling')
        })
    },
    disableFinding () {
      FindingsApi.disableFinding(this.name, this.selectedFinding.id)
        .then(() => {
          this.warning('Disable finding', 'Finding disabled successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger('Disable finding', 'Unexpected error in finding disabling')
        })
    },
    createTargetFromOSINT () {
      FindingsApi.createTargetFromOSINT(this.selectedFinding.id)
        .then(() => {
          this.success(this.selectedFinding.data, 'Target created successfully')
        })
        .catch(() => {
          this.danger(this.selectedFinding.data, 'Unexpected error in target creation')
        })
    },
    selectFinding (finding) {
      this.selectedFinding = finding
    },
    selectRow (items) {
      this.$emit('finding-selected', { type: this.name, finding: (items && items.length > 0) ? items[0] : null })
    },
    cleanSelection () {
      this.selectedFinding = null
    },
    displayRowDetails (row) {
      row._showDetails = !row._showDetails;
    }
  }
}
</script>
