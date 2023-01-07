<template>
  <div>
    <table-header :filters="filters" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="toolsFields" :items="data">
      <template #cell(icon)="row">
        <b-link :href="row.item.reference" target="_blank">
          <b-img v-if="row.item.icon" :src="row.item.icon" width="32"/>
          <b-img v-if="!row.item.icon" src="favicon.ico" width="32"/>
        </b-link>
      </template>
      <template #cell(stages)="row">
        <p>{{ Array.from(new Set(row.item.configurations.map(configuration => { return configuration.stage_name }))).join(', ') }}</p>
      </template>
      <template #cell(intensities)="row">
        <div v-for="base in intensityByVariant" v-bind:key="base.intensity_rank" class="d-inline">
          <div v-for="i in row.item.intensities" v-bind:key="i.intensity_rank" class="d-inline">
            <b-form-tag v-if="base.intensity_rank === i.intensity_rank" :variant="base.variant" v-b-tooltip.hover.top="i.intensity_rank" no-remove>{{ i.intensity_rank.charAt(0) }}</b-form-tag>
          </div>
        </div>
      </template>
      <template #cell(inputs)="row">
        <p>{{ Array.from(new Set(row.item.arguments.map(argument => { return argument.inputs.find(input => input.order === 1).type.name }))).join(', ') }}</p>
      </template>
      <template #cell(likes)="row">
        {{ row.item.likes }}
        <b-button variant="outline">
          <b-icon variant="danger" v-if="row.item.liked" icon="heart-fill" @click="dislikeTool(row.item.id)"/>
          <b-icon variant="danger" v-if="!row.item.liked" icon="heart" @click="likeTool(row.item.id)"/>
        </b-button>
      </template>
      <template #cell(actions)="row">
        <b-button @click="row.toggleDetails" variant="outline" class="mr-2" v-b-tooltip.hover title="Details">
          <b-icon v-if="!row.detailsShowing" variant="dark" icon="eye-fill"/>
          <b-icon v-if="row.detailsShowing" variant="secondary" icon="eye-slash-fill"/>
        </b-button>
        <b-button variant="outline" class="mr-2" v-b-tooltip.hover title="Execute" @click="taskModal(row.item)" v-b-modal.task-modal v-if="auditor.includes($store.state.role)">
          <b-icon variant="success" icon="play-circle-fill"/>
        </b-button>
        <b-dropdown variant="outline" right v-b-tooltip.hover title="Add to Process" v-if="auditor.includes($store.state.role)">
          <template #button-content>
            <b-icon variant="dark" icon="plus-square"/>
          </template>
          <b-dropdown-item @click="processModal(row.item)" v-b-modal.new-process-modal>New Process</b-dropdown-item>
          <b-dropdown-item @click="stepModal(row.item)" v-b-modal.new-step-modal>New Step</b-dropdown-item>
        </b-dropdown>
      </template>
      <template #row-details="row">
        <b-card>
          <b-table striped borderless small head-variant="light" :fields="configFields" :items="row.item.configurations">
            <template #cell(default)="config">
              <b-icon v-if="config.item.default" icon="check-circle-fill" variant="success"/>
            </template>
            <template #cell(outputs)="config">
              <p>{{ config.item.outputs.map(output => { return output.type.name }).join(', ') }}</p>
            </template>
          </b-table>
        </b-card>
      </template>
    </b-table>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="tools" @pagination="pagination"/>
    <process id="new-process-modal" :tool="selectedTool" :initialized="showProcessModal" @confirm="confirm" @clean="cleanSelection"/>
    <step id="new-step-modal" :tool="selectedTool" :initialized="showStepModal" @confirm="confirm" @clean="cleanSelection"/>
    <task id="task-modal" :tool="selectedTool" :initialized="showTaskModal" @clean="cleanSelection"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Pagination from '@/common/Pagination'
import TableHeader from '@/common/TableHeader'
import Process from '@/modals/Process'
import Step from '@/modals/Step'
import Task from '@/modals/Task'
export default {
  name: 'toolsPage',
  mixins: [RekonoApi],
  data () {
    this.fetchData()
    return {
      data: [],
      toolsFields: [
        { key: 'icon', label: '', sortable: false },
        { key: 'name', label: 'Tool', sortable: true },
        { key: 'command', sortable: true },
        { key: 'stages', label: 'Stages', sortable: false },
        { key: 'intensities', sortable: true },
        { key: 'inputs', sortable: false },
        { key: 'likes', sortable: true },
        { key: 'actions', sortable: false }
      ],
      configFields: [
        { key: 'name', label: 'Configuration', sortable: true },
        { key: 'default', sortable: true },
        { key: 'outputs', sortable: true }
      ],
      showTaskModal: false,
      showProcessModal: false,
      showStepModal: false,
      selectedTool: null,
      filters: []
    }
  },
  components: {
    Pagination,
    TableHeader,
    Process,
    Step,
    Task
  },
  watch: {
    data () {
      this.filters = [
        { name: 'Stage', values: this.stages, valueField: 'id', textField: 'value', filterField: 'stage' },
        { name: 'Input', values: this.inputTypes, valueField: 'value', textField: 'value', filterField: 'arguments__inputs__type__name' },
        { name: 'Output', values: this.inputTypes, valueField: 'value', textField: 'value', filterField: 'configurations__outputs__type__name' },
        { name: 'Favourities', type: 'checkbox', filterField: 'liked' }
      ] 
    }
  },
  methods: {
    fetchData (params = null) {
      if (!params) {
        params = {}
      }
      params['o'] = 'stage,name'
      return this.getOnePage('/api/tools/', params)
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    likeTool (toolId) {
      this.post(`/api/tools/${toolId}/like/`, { }).then(() => this.fetchData())
    },
    dislikeTool (toolId) {
      this.post(`/api/tools/${toolId}/dislike/`, { }).then(() => this.fetchData())
    },
    taskModal (tool) {
      this.cleanSelection()
      this.showTaskModal = true
      this.selectedTool = tool
    },
    processModal (tool) {
      this.cleanSelection()
      this.showProcessModal = true
      this.selectedTool = tool
    },
    stepModal (tool) {
      this.cleanSelection()
      this.showStepModal = true
      this.selectedTool = tool
    },
    cleanSelection () {
      this.showTaskModal = false
      this.showProcessModal = false
      this.showStepModal = false
      this.selectedTool = null
    }
  }
}
</script>
