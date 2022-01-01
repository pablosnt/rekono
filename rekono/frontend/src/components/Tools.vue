<template>
  <div>
    <TableHeader :filters="filters" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="toolsFields" :items="tools">
      <template #cell(icon)="row">
        <b-link :href="row.item.reference" target="_blank">
          <b-img :src="row.item.icon" width="100" height="50"/>
        </b-link>
      </template>
      <template #cell(intensities)="row">
        <div v-for="base in intensities" v-bind:key="base.intensity_rank" class="d-inline">
          <div v-for="i in row.item.intensities" v-bind:key="i.intensity_rank" class="d-inline">
            <b-form-tag v-if="base.intensity_rank === i.intensity_rank" :variant="base.variant" v-b-tooltip.hover.top="i.intensity_rank" no-remove>{{ i.intensity_rank.charAt(0) }}</b-form-tag>
          </div>
        </div>
      </template>
      <template #cell(actions)="row">
        <b-button @click="row.toggleDetails" variant="dark" class="mr-2" v-b-tooltip.hover title="Details">
          <b-icon v-if="!row.detailsShowing" icon="eye-fill"/>
          <b-icon v-if="row.detailsShowing" icon="eye-slash-fill"/>
        </b-button>
        <b-button variant="success" class="mr-2" v-b-tooltip.hover title="Execute" @click="showExecuteForm(row.item)" v-b-modal.execute-modal>
          <b-icon icon="play-fill"/>
        </b-button>
        <b-dropdown variant="outline-primary" right v-b-tooltip.hover title="Add to Process">
          <template #button-content>
            <b-icon icon="plus-square"/>
          </template>
          <b-dropdown-item @click="showProcessForm(row.item)" v-b-modal.new-process-modal >New Process</b-dropdown-item>
          <b-dropdown-item @click="showStepForm(row.item)" v-b-modal.new-step-modal>New Step</b-dropdown-item>
        </b-dropdown>
      </template>
      <template #row-details="row">
        <b-card>
          <b-table striped borderless small head-variant="light" :fields="configFields" :items="row.item.configurations">
            <template #cell(default)="config">
              <b-icon v-if="config.item.default" icon="check-circle-fill" variant="success"/>
            </template>
            <template #cell(inputs)="config">
              <p>{{ config.item.inputs.map((input) => { return input.type }).join(', ') }}</p>
            </template>
            <template #cell(outputs)="config">
              <p>{{ config.item.outputs.map((output) => { return output.type }).join(', ') }}</p>
            </template>
          </b-table>
        </b-card>
      </template>
    </b-table>
    <Pagination :page="page" :limit="limit" :limits="limits" :total="total" name="tools" @pagination="pagination"/>
    <ProcessForm id="new-process-modal" :tool="selectedTool" :initialized="processForm" @confirm="confirm" @clean="cleanSelection"/>
    <StepForm id="new-step-modal" :tool="selectedTool" :initialized="stepForm" @confirm="confirm" @clean="cleanSelection"/>
    <TaskForm id="execute-modal" :tool="selectedTool" :initialized="taskForm" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import ToolApi from '@/backend/tools'
import { stages, findingTypes, auditor, intensitiesByVariant } from '@/backend/constants'
import Pagination from '@/common/Pagination.vue'
import TableHeader from '@/common/TableHeader.vue'
import PaginationMixin from '@/common/mixin/PaginationMixin.vue'
import ProcessForm from '@/modals/ProcessForm.vue'
import StepForm from '@/modals/StepForm.vue'
import TaskForm from '@/modals/TaskForm.vue'
export default {
  name: 'toolsPage',
  mixins: [PaginationMixin],
  data () {
    return {
      auditor: auditor,
      intensities: intensitiesByVariant,
      tools: this.fetchData(),
      toolsFields: [
        { key: 'icon', sortable: false },
        { key: 'name', label: 'Tool', sortable: true },
        { key: 'command', sortable: true },
        { key: 'stage_name', label: 'Stage', sortable: true },
        { key: 'intensities', sortable: true },
        { key: 'actions', sortable: false }
      ],
      configFields: [
        { key: 'name', label: 'Configuration', sortable: true },
        { key: 'default', sortable: true },
        { key: 'inputs', sortable: true },
        { key: 'outputs', sortable: true }
      ],
      taskForm: false,
      processForm: false,
      stepForm: false,
      selectedTool: null,
      filters: []
    }
  },
  components: {
    Pagination,
    ProcessForm,
    StepForm,
    TableHeader,
    TaskForm
  },
  watch: {
    tools () {
      this.filters = [
        { name: 'Stage', values: stages, valueField: 'id', textField: 'value', filterField: 'stage' },
        { name: 'Input', values: findingTypes, valueField: 'value', textField: 'value', filterField: 'configurations__inputs__type' },
        { name: 'Output', values: findingTypes, valueField: 'value', textField: 'value', filterField: 'configurations__outputs__type' }
      ] 
    }
  },
  methods: {
    fetchData (filter = null) {
      ToolApi.getTools(this.getPage(), this.getLimit(), filter)
        .then(data => {
          this.total = data.count
          this.tools = data.results
        })
    },
    showExecuteForm (tool) {
      this.taskForm = true
      this.selectTool(tool)
    },
    showProcessForm (tool) {
      this.processForm = true
      this.selectTool(tool)
    },
    showStepForm (tool) {
      this.stepForm = true
      this.selectTool(tool)
    },
    selectTool (tool) {
      this.selectedTool = tool
    },
    cleanSelection () {
      this.taskForm = false
      this.processForm = false
      this.stepForm = false
      this.selectedTool = null
    }
  }
}
</script>
