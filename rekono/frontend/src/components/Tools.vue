<template>
  <div>
    <b-table striped borderless head-variant="dark" :fields="toolsFields" :items="tools">
      <template #cell(icon)="row">
        <b-link :href="row.item.reference" target="_blank">
          <b-img :src="row.item.icon" width="100" height="50"/>
        </b-link>
      </template>
      <template #cell(intensities)="row">
        <div v-for="item in row.item.intensities" v-bind:key="item.value" style="display: inline">
          <b-badge :variant="item.variant" v-b-tooltip.hover :title="item.value">{{ item.summary }}</b-badge>
          <span/>
        </div>
      </template>
      <template #cell(actions)="row">
        <b-button @click="row.toggleDetails" variant="dark" class="mr-2" v-b-tooltip.hover title="Details">
          <b-icon v-if="!row.detailsShowing" icon="eye-fill"/>
          <b-icon v-if="row.detailsShowing" icon="eye-slash-fill"/>
        </b-button>
        <b-button variant="success" class="mr-2" v-b-tooltip.hover title="Execute" @click="selectTool(row.item)" v-b-modal.execute-modal>
          <b-icon icon="play-fill"/>
        </b-button>
        <b-dropdown variant="outline-primary" right v-b-tooltip.hover title="Add to Process">
          <template #button-content>
            <b-icon icon="plus-square"/>
          </template>
          <b-dropdown-item @click="selectTool(row.item)" v-b-modal.new-process-modal >New Process</b-dropdown-item>
          <b-dropdown-item @click="selectTool(row.item)" v-b-modal.new-step-modal>New Step</b-dropdown-item>
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
    <ProcessForm id="new-process-modal"
      :tool="selectedTool"
      @confirm="confirm"
      @clean="cleanSelection"/>
    <StepForm id="new-step-modal"
      :tool="selectedTool"
      @confirm="confirm"
      @clean="cleanSelection"/>
    <TaskForm id="execute-modal"
      :tool="selectedTool"
      @confirm="confirm"
      @clean="cleanSelection"/>
  </div>
</template>

<script>
import { getTools } from '../backend/tools'
import ProcessForm from './forms/ProcessForm.vue'
import StepForm from './forms/StepForm.vue'
import TaskForm from './forms/TaskForm.vue'
export default {
  name: 'toolsPage',
  data () {
    return {
      auditor: ['Admin', 'Auditor'],
      tools: this.getTools(),
      toolsFields: [
        {key: 'icon', sortable: false},
        {key: 'name', label: 'Tool', sortable: true},
        {key: 'command', sortable: true},
        {key: 'stage_name', label: 'Stage', sortable: true},
        {key: 'intensities', sortable: true},
        {key: 'actions', sortable: false}
      ],
      configFields: [
        {key: 'name', label: 'Configuration', sortable: true},
        {key: 'default', sortable: true},
        {key: 'inputs_text', label: 'Inputs', sortable: true},
        {key: 'outputs_text', label: 'Outputs', sortable: true}
      ],
      selectedTool: null
    }
  },
  components: {
    ProcessForm,
    StepForm,
    TaskForm
  },
  methods: {
    getTools () {
      getTools()
        .then(tools => {
          for (var t = 0; t < tools.length; t++) {
            var intensities = []
            for (var i = 0; i < tools[t].intensities.length; i++) {
              var value = tools[t].intensities[i].intensity_rank
              var variant = 'secondary'
              if (value === 'Sneaky') variant = 'info'
              else if (value === 'Low') variant = 'success'
              else if (value === 'Hard') variant = 'warning'
              else if (value === 'Insane') variant = 'danger'
              var intensity = {
                variant: variant,
                value: value,
                summary: value.charAt(0).toUpperCase()
              }
              intensities.push(intensity)
            }
            tools[t].intensities = intensities
            for (var c = 0; c < tools[t].configurations.length; c++) {
              var inputsText = ''
              for (i = 0; i < tools[t].configurations[c].inputs.length; i++) {
                inputsText += tools[t].configurations[c].inputs[i].type
                if (i + 1 < tools[t].configurations[c].inputs.length) {
                  inputsText += ', '
                }
              }
              var outputsText = ''
              for (var o = 0; o < tools[t].configurations[c].outputs.length; o++) {
                outputsText += tools[t].configurations[c].outputs[o].type
                if (o + 1 < tools[t].configurations[c].outputs.length) {
                  outputsText += ', '
                }
              }
              tools[t].configurations[c].inputs_text = inputsText
              tools[t].configurations[c].outputs_text = outputsText
            }
          }
          this.tools = tools
        })
    },
    selectTool (tool) {
      this.selectedTool = tool
    },
    confirm (operation) {
      if (operation.success) {
        this.$bvModal.hide(operation.id)
        if (operation.reload) {
          this.tools = this.getTools()
        }
      }
    },
    cleanSelection () {
      this.selectedTool = null
    }
  }
}
</script>
