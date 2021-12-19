<template>
  <div>
    <TableHeader search="name" :filters="filters" add="wordlist-modal" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="wordlistsFields" :items="wordlists">
      <template #cell(actions)="row">
        <b-dropdown variant="outline-primary" right>
          <template #button-content>
            <b-icon icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item variant="dark" @click="selectWordlist(row.item)" v-b-modal.wordlist-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
            <b-icon icon="pencil-square"/>
            <label class="ml-1">Edit</label>
          </b-dropdown-item>
          <b-dropdown-item variant="danger" @click="selectWordlist(row.item)" v-b-modal.delete-wordlist-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
            <b-icon icon="trash-fill"/>
            <label class="ml-1">Delete</label>
          </b-dropdown-item>
        </b-dropdown>
      </template>
    </b-table>
    <Pagination :page="page" :size="size" :sizes="sizes" :total="total" name="wordlists" @pagination="pagination"/>
    <Deletion id="delete-wordlist-modal"
      title="Delete Wordlist"
      @deletion="deleteWordlist"
      @clean="cleanSelection"
      v-if="selectedWordlist !== null && selectedWordlist !== null">
      <span><strong>{{ this.selectedWordlist.name }}</strong> wordlist</span>
    </Deletion>
    <WordlistForm id="wordlist-modal" :wordlist="selectedWordlist" :initialized="selectedWordlist !== null" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import WordlistApi from '@/backend/resources'
import Deletion from '@/common/Deletion.vue'
import TableHeader from '@/common/TableHeader.vue'
import Pagination from '@/common/Pagination.vue'
import PaginationMixin from '@/common/mixin/PaginationMixin.vue'
import WordlistForm from '@/forms/WordlistForm.vue'
export default {
  name: 'wordlistsPage',
  mixins: [PaginationMixin],
  data () {
    return {
      wordlists: this.fetchData(),
      wordlistsFields: [
        { key: 'name', label: 'Wordlist', sortable: true },
        { key: 'type', sortable: true },
        { key: 'size', sortable: true },
        { key: 'creator.username', label: 'Creator', sortable: true },
        { key: 'actions', sortable: false }
      ],
      selectedWordlist: null,
      filters: []
    }
  },
  components: {
    Deletion,
    TableHeader,
    Pagination,
    WordlistForm
  },
  watch: {
    wordlists (wordlists) {
      const creators = []
      const unique = []
      for (let i = 0; i < wordlists.length; i++) {
        if (wordlists[i].creator.id && !unique.includes(wordlists[i].creator.id)) {
          creators.push(wordlists[i].creator)
          unique.push(wordlists[i].creator.id)
        }
      }
      this.filters = [
        { name: 'Type', values: ['Endpoint', 'Password'], valueField: 'value', textField: 'value', filterField: 'type' },
        { name: 'Creator', values: creators, default: unique.includes(this.$store.state.user) ? this.$store.state.user : null, valueField: 'id', textField: 'username', filterField: 'creator' }
      ] 
    }
  },
  methods: {
    fetchData (filter = null) {
      WordlistApi.getAllWordlists(this.getPage(), this.getSize(), filter).then(wordlists => { this.wordlists = wordlists })
    },
    deleteWordlist () {
      WordlistApi.deleteWordlist(this.selectedWordlist.id)
        .then(() => {
          this.$bvModal.hide('delete-wordlist-modal')
          this.$bvToast.toast('Wordlist deleted successfully', {
            title: this.selectedWordlist.name,
            variant: 'warning',
            solid: true
          })
          this.fetchData()
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in wordlist deletion', {
            title: this.selectedWordlist.name,
            variant: 'danger',
            solid: true
          })
        })
    },
    selectWordlist (wordlist) {
      this.selectedWordlist = wordlist
    },
    cleanSelection () {
      this.selectedWordlist = null
    }
  }
}
</script>
