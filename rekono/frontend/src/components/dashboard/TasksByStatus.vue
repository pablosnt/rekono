<script>
import { Doughnut } from 'vue-chartjs'
import { statuses } from '@/backend/constants'
export default {
  extends: Doughnut,
  props: {
    requested: Number,
    skipped: Number,
    running: Number,
    cancelled: Number,
    error: Number,
    completed: Number
  },
  computed: {
    total () {
      return this.requested + this.skipped + this.running + this.cancelled + this.error + this.completed
    }
  },
  watch: {
    total () {
      this.renderChart({
        labels: statuses,
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
