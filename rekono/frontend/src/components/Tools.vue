<template>
  <div>
    <b-table striped borderless head-variant="dark" :fields="toolsFields" :items="toolsItems">
      <template #cell(icon)="row">
        <b-link :href="row.item.reference" target="_blank">
          <b-img :src="row.item.icon" width="100" height="50"/>
        </b-link>
      </template>
      <template #cell(actions)="row">
        <b-button @click="row.toggleDetails" variant="dark" class="mr-2">
          <b-icon v-if="!row.detailsShowing" icon="eye-fill"/>
          <b-icon v-if="row.detailsShowing" icon="eye-slash-fill"/>
        </b-button>
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
  </div>
</template>

<script>
import { getTools } from '../backend/tools'
export default {
  name: 'toolsPage',
  data () {
    var items = []
    getTools()
      .then(results => {
        for (var i = 0; i < results.length; i++) {
          var configurations = []
          for (var c = 0; c < results[i].configurations.length; c++) {
            var inputs = ''
            for (var j = 0; j < results[i].configurations[c].inputs.length; j++) {
              inputs += results[i].configurations[c].inputs[j].type
              if (j + 1 < results[i].configurations[c].inputs.length) {
                inputs += ', '
              }
            }
            var outputs = ''
            for (j = 0; j < results[i].configurations[c].outputs.length; j++) {
              outputs += results[i].configurations[c].outputs[j].type
              if (j + 1 < results[i].configurations[c].outputs.length) {
                outputs += ', '
              }
            }
            var config = {
              name: results[i].configurations[c].name,
              inputs: inputs,
              outputs: outputs,
              default: results[i].configurations[c].default
            }
            configurations.push(config)
          }
          var item = {
            id: results[i].id,
            name: results[i].name,
            command: results[i].command,
            stage: results[i].stage_name,
            icon: results[i].icon,
            reference: results[i].reference,
            configurations: configurations
          }
          items.push(item)
        }
      })
    return {
      toolsItems: items,
      toolsFields: ['icon', 'name', 'command', 'stage', 'actions'],
      configFields: ['name', 'default', 'inputs', 'outputs']
    }
  }
}
</script>

<style scoped>
</style>
