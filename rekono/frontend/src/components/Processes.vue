<template>
  <div>
    <div class="text-right">
      <b-button size="lg" variant="outline" v-b-modal.new-process-modal>
        <p class="h2 mb-2"><b-icon variant="success" icon="plus-square-fill"/></p>
      </b-button>
    </div>
    <b-table striped borderless head-variant="dark" :fields="processesFields" :items="processesItems">
      <template #cell(actions)="row">
          <b-button @click="row.toggleDetails" variant="dark" class="mr-2">
            <b-icon v-if="!row.detailsShowing" icon="eye-fill"/>
            <b-icon v-if="row.detailsShowing" icon="eye-slash-fill"/>
          </b-button>
        </template>
        <template #row-details="row">
          <b-card>
            <p>{{ row.item.details.description }}</p>
            <b-table striped borderless small head-variant="light" :fields="stepsFields" :items="row.item.details.steps">
              <template #cell(icon)="step">
                <b-link :href="step.item.reference" target="_blank">
                  <b-img :src="step.item.icon" width="100" height="50"/>
                </b-link>
              </template>
            </b-table>
          </b-card>
        </template>
    </b-table>
    <b-modal id="new-process-modal" @hidden="resetModal" @ok="handleNewProcess" title="New Process" ok-title="Create Process">
      <b-form ref="new_process_form" @submit.stop.prevent="createNewProcess">
        <b-form-group description="Process name" invalid-feedback="Process name is required">
          <b-form-input v-model="processName" type="text" :state="newProcessNameState" maxlength="30" required/>
        </b-form-group>
        <b-form-group invalid-feedback="Process description is required">
          <b-form-textarea v-model="processDescription" placeholder="Process description" :state="newProcessDescState" maxlength="350" required/>
        </b-form-group>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import { getAllProcesses, createNewProcess } from '../backend/processes'
export default {
  name: 'processesPage',
  data () {
    return {
      processesItems: this.processes(),
      processesFields: [
        {key: 'process', sortable: true},
        {key: 'steps', sortable: true},
        {key: 'creator', sortable: true},
        {key: 'actions', sortable: false}
      ],
      stepsFields: [
        {key: 'icon', sortable: false},
        {key: 'tool', sortable: true},
        {key: 'configuration', sortable: true},
        {key: 'stage', sortable: true},
        {key: 'priority', sortable: true}
      ],
      processName: null,
      processDescription: null,
      newProcessNameState: null,
      newProcessDescState: null
    }
  },
  methods: {
    processes () {
      var processes = []
      getAllProcesses()
        .then(results => {
          for (var i = 0; i < results.length; i++) {
            var steps = []
            for (var s = 0; s < results[i].steps.length; s++) {
              var step = {
                icon: results[i].steps[s].tool.icon,
                reference: results[i].steps[s].tool.reference,
                tool: results[i].steps[s].tool.name,
                configuration: results[i].steps[s].configuration.name,
                stage: results[i].steps[s].tool.stage_name,
                priority: results[i].steps[s].priority
              }
              steps.push(step)
            }
            var item = {
              process: results[i].name,
              creator: results[i].creator,
              steps: results[i].steps.length,
              details: {
                description: results[i].description,
                steps: steps
              }
            }
            processes.push(item)
          }
        })
      return processes
    },
    handleNewProcess (bvModalEvt) {
      bvModalEvt.preventDefault()
      this.createNewProcess()
    },
    createNewProcess () {
      if (!this.checkNewProcessState()) {
        return
      }
      createNewProcess(this.processName, this.processDescription)
        .then(data => {
          this.$bvModal.hide('new-process-modal')
          this.$bvToast.toast('New process created successfully', {
            title: this.processName,
            variant: 'success',
            solid: true
          })
          this.processesItems = this.processes()
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in process creation', {
            title: this.processName,
            variant: 'danger',
            solid: true
          })
        })
    },
    checkNewProcessState () {
      const valid = this.$refs.new_process_form.checkValidity()
      this.newProcessNameState = (this.processDescription != null)
      this.newProcessDescState = (this.processName != null)
      return valid
    },
    resetModal () {
      this.processName = null
      this.processDescription = null
      this.newProcessNameState = null
      this.newProcessDescState = null
    }
  }
}
</script>
