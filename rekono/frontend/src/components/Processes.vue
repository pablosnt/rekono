<template>
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
</template>

<script>
import { getAllProcesses } from '../backend/processes'
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
      ]
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
    }
  }
}
</script>
