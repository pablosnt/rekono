<template>
  <div>
    <b-table striped borderless head-variant="dark" :fields="toolsFields" :items="toolsItems">
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
      @cancel="cleanSelection"/>
    <StepForm id="new-step-modal"
      :tool="selectedTool"
      @confirm="confirm"
      @cancel="cleanSelection"/>
    <TaskForm id="execute-modal"
      :tool="selectedTool"
      @confirm="confirm"
      @cancel="cleanSelection"/>
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
      toolsItems: this.tools(),
      toolsFields: [
        {key: 'icon', sortable: false},
        {key: 'name', label: 'Tool', sortable: true},
        {key: 'command', sortable: true},
        {key: 'stage', sortable: true},
        {key: 'intensities', sortable: true},
        {key: 'actions', sortable: false}
      ],
      configFields: [
        {key: 'name', label: 'Configuration', sortable: true},
        {key: 'default', sortable: true},
        {key: 'inputs', sortable: true},
        {key: 'outputs', sortable: true}
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
    tools () {
      var tools = []
      getTools()
        .then(results => {
          for (var i = 0; i < results.length; i++) {
            var configurations = []
            for (var c = 0; c < results[i].configurations.length; c++) {
              var inputsText = ''
              for (var j = 0; j < results[i].configurations[c].inputs.length; j++) {
                inputsText += results[i].configurations[c].inputs[j].type
                if (j + 1 < results[i].configurations[c].inputs.length) {
                  inputsText += ', '
                }
              }
              var outputsText = ''
              for (j = 0; j < results[i].configurations[c].outputs.length; j++) {
                outputsText += results[i].configurations[c].outputs[j].type
                if (j + 1 < results[i].configurations[c].outputs.length) {
                  outputsText += ', '
                }
              }
              var config = {
                id: results[i].configurations[c].id,
                name: results[i].configurations[c].name,
                default: results[i].configurations[c].default,
                inputs: results[i].configurations[c].inputs,
                inputs_text: inputsText,
                outputs: results[i].configurations[c].outputs,
                outputs_text: outputsText
              }
              configurations.push(config)
            }
            var intensities = []
            for (j = 0; j < results[i].intensities.length; j++) {
              var value = results[i].intensities[j].intensity_rank
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
            var item = {
              id: results[i].id,
              name: results[i].name,
              command: results[i].command,
              stage: results[i].stage_name,
              icon: results[i].icon,
              reference: results[i].reference,
              configurations: configurations,
              intensities: intensities
            }
            tools.push(item)
          }
        })
      return tools
    },
    selectTool (tool) {
      this.selectedTool = tool
    },
    confirm (operation) {
      if (operation.success) {
        this.$bvModal.hide(operation.id)
        this.toolsItems = this.tools()
      }
    },
    cleanSelection () {
      this.selectedTool = null
    }
  }
}
</script>
