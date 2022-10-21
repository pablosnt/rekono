<script>
import RekonoApi from '@/backend/RekonoApi';
export default {
  name: 'projectsPage',
  mixins: [RekonoApi],
  data () {
    return {
        defectDojoUrl: this.getDefectDojoUrl(),
        defectDojoEnabled: this.isDefectDojoEnabled()
    }
  },
  methods: {
    getDefectDojoUrl () {
        this.get('/api/settings/3/').then(response => this.defectDojoUrl = response.data.value)
    },
    isDefectDojoEnabled () {
        this.get('/api/settings/defectdojo/').then(response => this.defectDojoEnabled = response.status === 200)
    }
  }
}
</script>