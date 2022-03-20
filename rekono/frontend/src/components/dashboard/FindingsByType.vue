<script>
import { Doughnut } from 'vue-chartjs'
export default {
  extends: Doughnut,
  props: {
    osint: Number,
    credentials: Number,
    hosts: Number,
    ports: Number,
    paths: Number,
    technologies: Number,
    vulnerabilities: Number,
    exploits: Number
  },
  computed: {
    total () {
      return this.osint + this.credentials + this.hosts + this.ports + this.paths + this.technologies + this.vulnerabilities + this.exploits
    }
  },
  watch: {
    total () {
      this.renderChart({
        labels: ['OSINT', 'Credentials', 'Hosts', 'Ports', 'Paths', 'Technologies', 'Vulnerabilities', 'Exploits'],
        datasets: [
          {
            backgroundColor: ['black', 'gray', 'blue', 'green', 'purple', 'gold', 'orange', 'red'],
            data: [this.osint, this.credentials, this.hosts, this.ports, this.paths, this.technologies, this.vulnerabilities, this.exploits]
          }
        ]
      },
      {
        title: {
          display: true,
          text: 'Findings by type'
        }
      })
    }
  }
}
</script>
