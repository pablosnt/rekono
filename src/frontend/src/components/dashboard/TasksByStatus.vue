<script>
import { Doughnut } from 'vue-chartjs'
import RekonoApi from '@/backend/RekonoApi'
export default {
  extends: Doughnut,
  mixins: [RekonoApi],
  props: {
    requested: Number,
    skipped: Number,
    running: Number,
    cancelled: Number,
    error: Number,
    completed: Number
  },
  computed: {
    totalTasks () {
      return this.requested + this.skipped + this.running + this.cancelled + this.error + this.completed
    }
  },
  watch: {
    totalTasks () {
      this.renderChart({
        labels: this.statuses,
        datasets: [
          {
            backgroundColor: ['blue', 'gray', 'gold', 'black', 'red', 'green'],
            data: [this.requested, this.skipped, this.running, this.cancelled, this.error, this.completed]
          }
        ]
      },
      {
        title: {
          display: true,
          text: 'Tasks by status'
        }
      })
    }
  }
}
</script>
