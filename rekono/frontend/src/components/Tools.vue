<template>
  <div>
    <TableHeader search="name" :filters="filters" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="toolsFields" :items="tools">
      <template #cell(icon)="row">
        <b-link :href="row.item.reference" target="_blank">
          <b-img :src="row.item.icon" width="100" height="50"/>
        </b-link>
      </template>
      <template #cell(intensities)="row">
        <b-form-tag v-for="item in row.item.intensities" v-bind:key="item.value" :variant="item.variant" v-b-tooltip.hover.top="item.value" no-remove>{{ item.summary }}</b-form-tag>
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
import { stages, findingTypes } from '@/backend/constants'
import Pagination from '@/common/Pagination.vue'
import TableHeader from '@/common/TableHeader.vue'
import PaginationMixin from '@/common/mixin/PaginationMixin.vue'
import ProcessForm from '@/forms/ProcessForm.vue'
import StepForm from '@/forms/StepForm.vue'
import TaskForm from '@/forms/TaskForm.vue'
export default {
  name: 'toolsPage',
  mixins: [PaginationMixin],
  data () {
    return {
      auditor: ['Admin', 'Auditor'],
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
        { key: 'inputs_text', label: 'Inputs', sortable: true },
        { key: 'outputs_text', label: 'Outputs', sortable: true }
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
        { name: 'Configuration', filterField: 'configuration__name__icontains', type: 'text'},
        { name: 'Input', values: findingTypes, valueField: 'value', textField: 'value', filterField: 'input' },
        { name: 'Output', values: findingTypes, valueField: 'value', textField: 'value', filterField: 'output' }
      ] 
    }
  },
  methods: {
    fetchData (filter = null) {
      ToolApi.getTools(this.getPage(), this.getLimit(), filter)
        .then(data => {
          this.total = data.count
          for (let t = 0; t < data.results.length; t++) {
            const intensities = []
            for (let i = 0; i < data.results[t].intensities.length; i++) {
              const value = data.results[t].intensities[i].intensity_rank
              let variant = 'secondary'
              if (value === 'Sneaky') variant = 'info'
              else if (value === 'Low') variant = 'success'
              else if (value === 'Hard') variant = 'warning'
              else if (value === 'Insane') variant = 'danger'
              const intensity = {
                variant: variant,
                value: value,
                summary: value.charAt(0).toUpperCase()
              }
              intensities.push(intensity)
            }
            data.results[t].intensities = intensities
            for (let c = 0; c < data.results[t].configurations.length; c++) {
              let inputsText = ''
              for (let i = 0; i < data.results[t].configurations[c].inputs.length; i++) {
                inputsText += data.results[t].configurations[c].inputs[i].type
                if (i + 1 < data.results[t].configurations[c].inputs.length) {
                  inputsText += ', '
                }
              }
              let outputsText = ''
              for (let o = 0; o < data.results[t].configurations[c].outputs.length; o++) {
                outputsText += data.results[t].configurations[c].outputs[o].type
                if (o + 1 < data.results[t].configurations[c].outputs.length) {
                  outputsText += ', '
                }
              }
              data.results[t].configurations[c].inputs_text = inputsText
              data.results[t].configurations[c].outputs_text = outputsText
            }
          }
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
