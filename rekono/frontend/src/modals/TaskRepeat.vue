<template>
  <b-modal :id="id" @ok="confirm" title="Repeat Task" ok-title="Execute Now" header-bg-variant="success" header-text-variant="light" ok-variant="success">
    <p>This task will be executed right now. Are you sure?</p>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'repeatTaskModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    task: Object
  },
  methods: {
    confirm (event) {
      event.preventDefault()
      this.post(`/api/tasks/${this.task.id}/repeat/`, { }, this.task.process ? this.task.process.name : this.task.tool.name, 'Task executed again successfully')
        .then(data => {
          this.$bvModal.hide(this.id)
          this.$router.push({ name: 'task', params: { id: data.id, task: data } })
        })
    }
  }
}
</script>
