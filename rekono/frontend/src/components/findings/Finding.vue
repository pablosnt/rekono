<template>
  <b-col v-if="findings && findings.length > 0 && (selectedFindingTypes.length === 0 || selectedFindingTypes.includes(name.toLowerCase()))">
    <b-table select-mode="single" :selectable="details !== null" hover striped borderless head-variant="dark" :fields="fields" :items="findings" @row-clicked="displayRowDetails" @row-selected="selectFinding">
      <template #row-details="row">
        <!-- <b-col> -->
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
      </template>
    </b-table>
  </b-col>
</template>

<script>
import FindingApi from '@/backend/findings'
export default {
  name: 'findingBase',
  props: ['name', 'fields', 'findingTypes', 'target', 'task', 'search', 'selection', 'details'],
  computed: {
    filterChange () {
      return this.findingTypes.toString() + this.target + this.task + this.search + JSON.stringify(this.selection)
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
      findings: []
    }
  },
  watch: {
    filterChange () {
      this.fetchData()
    }
  },
  methods: {
    getFilter () {
      let filter = {}
      if (this.target) {
        filter.execution__task__target = this.target
      } else if (this.task) {
        filter.execution__task = this.task
      }
      if (this.search) {
        filter.search = this.search
      }
      if (!this.selectedFindingTypes.includes(this.name.toLowerCase()) && this.selection) {
        filter = Object.assign({}, filter, this.selection)
      }
      return filter
    },
    fetchData () {
      if ((this.task || this.target) && (this.selectedFindingTypes.length === 0 || this.selectedFindingTypes.includes(this.name.toLowerCase()))) {
        FindingApi.getAllFindings(this.name.toLowerCase(), this.getFilter())
          .then(results => {
            this.findings = results
          })
      }
    },
    selectFinding (items) {
      this.$emit('finding-selected', { type: this.name, finding: (items && items.length > 0) ? items[0] : null })
    },
    displayRowDetails (row) {
      row._showDetails = !row._showDetails;
    }
  }
}
</script>
