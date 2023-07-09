<script>
import { Bar } from 'vue-chartjs'
export default {
  extends: Bar,
  props: {
    label: String,
    critical: Number,
    high: Number,
    medium: Number,
    low: Number,
    info: Number
  },
  mounted () {
    this.renderChart({
        labels: ['Vulnerabilities'],
        datasets: [
          {
            label: 'Critical',
            backgroundColor: 'red',
            data: [this.critical]
          },
          {
            label: 'High',
            backgroundColor: 'orange',
            data: [this.high]
          },
          {
            label: 'Medium',
            backgroundColor: 'gold',
            data: [this.medium]
          },
          {
            label: 'Low',
            backgroundColor: 'blue',
            data: [this.low]
          },
          {
            label: 'Info',
            backgroundColor: 'green',
            data: [this.info]
          }
        ]
      },
      {
        maintainAspectRatio: false,
        scales: {
          yAxes: [{
            ticks: {
              stepSize: 1
            }
          }]
        },
        title: {
          display: true,
          text: this.label
        }
      })
  }
}
</script>
