<script>
import { Doughnut } from 'vue-chartjs'
export default {
  extends: Doughnut,
  props: {
    osint: Number,
    credentials: Number,
    hosts: Number,
    enumerations: Number,
    endpoints: Number,
    technologies: Number,
    vulnerabilities: Number,
    exploits: Number
  },
  computed: {
    total () {
      return this.osint + this.credentials + this.hosts + this.enumerations + this.endpoints + this.technologies + this.vulnerabilities + this.exploits
    }
  },
  watch: {
    total () {
      this.renderChart({
        labels: ['OSINT', 'Credentials', 'Hosts', 'Enumerations', 'Endpoints', 'Technologies', 'Vulnerabilities', 'Exploits'],
        datasets: [
          {
            backgroundColor: ['black', 'gray', 'blue', 'green', 'purple', 'gold', 'orange', 'red'],
            data: [this.osint, this.credentials, this.hosts, this.enumerations, this.endpoints, this.technologies, this.vulnerabilities, this.exploits]
          }
        ]
      })
    }
  }
}
</script>
