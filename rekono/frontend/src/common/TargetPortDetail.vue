<template>
  <div>
    <authentication  v-if="name === 'authentication'" :targetPortId="targetPortId" @update="fetchData()"/>
    <target-technology  v-if="name === 'technology'" :targetPortId="targetPortId" @update="fetchData()"/>
    <target-vulnerability v-if="name === 'vulnerability'" :targetPortId="targetPortId" @update="fetchData()"/>
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
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" :name="endpoint.replace('target-', '')" @pagination="pagination"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import Pagination from '@/common/Pagination'
import Authentication from '@/modals/Authentication'
import TargetTechnology from '@/modals/TargetTechnology'
import TargetVulnerability from '@/modals/TargetVulnerability'
export default {
  name: 'targetPortDetail',
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
    Pagination,
    TargetVulnerability,
    TargetTechnology,
    Authentication
  },
  data () {
    this.fetchData()
    return {
      limit: 10,
      limits: [10, 25, 50, 100],
      data: [],
      selectedItem: null
    }
  },
  methods: {
    fetchData () {
      return this.getOnePage(`/api/${this.endpoint}/?o=${this.field}`, { target_port: this.targetPortId })
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    deleteItem () {
      this.delete(`/api/${this.endpoint}/${this.selectedItem.id}/`).then(() => this.fetchData())
    },
    selectItem (item) {
      this.selectedItem = item
    },
    cleanSelection () {
      this.selectedItem = null
    }
  }
}
</script>