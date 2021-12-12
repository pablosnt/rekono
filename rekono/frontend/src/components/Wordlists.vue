<template>
  <div>
    <div class="text-right">
      <b-button size="lg" variant="outline" v-b-modal.wordlist-modal>
        <p class="h2 mb-2"><b-icon variant="success" icon="plus-square-fill"/></p>
      </b-button>
    </div>
    <b-table striped borderless head-variant="dark" :fields="wordlistsFields" :items="wordlists">
      <template #cell(actions)="row">
        <b-dropdown variant="outline-primary" right>
          <template #button-content>
            <b-icon icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item variant="dark" @click="selectWordlist(row.item)" v-b-modal.wordlist-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
            <b-icon icon="pencil-square"/>
            <label>Edit</label>
          </b-dropdown-item>
          <b-dropdown-item variant="danger" @click="selectWordlist(row.item)" v-b-modal.delete-wordlist-modal :disabled="$store.state.role !== 'Admin' && $store.state.user !== row.item.creator.id">
            <b-icon icon="trash-fill"/>
            <label>Delete</label>
          </b-dropdown-item>
        </b-dropdown>
      </template>
    </b-table>
    <Pagination :page="page" :size="size" :sizes="sizes" :total="total" name="wordlists" @pagination="pagination"/>
    <DeleteConfirmation id="delete-wordlist-modal"
      title="Delete Wordlist"
      @deletion="deleteWordlist"
      @clean="cleanSelection"
      v-if="selectedWordlist !== null && selectedWordlist !== null">
      <span slot="body"><strong>{{ this.selectedWordlist.name }}</strong> wordlist</span>
    </DeleteConfirmation>
    <WordlistForm id="wordlist-modal" :wordlist="selectedWordlist" @confirm="confirm" @clean="cleanSelection"/>
  </div>
</template>

<script>
import WordlistApi from '../backend/resources'
import DeleteConfirmation from './common/DeleteConfirmation.vue'
import WordlistForm from './forms/WordlistForm.vue'
import Pagination from './common/Pagination.vue'
import PaginationMixin from './common/PaginationMixin.vue'
export default {
  name: 'wordlistsPage',
  mixins: [PaginationMixin],
  data () {
    return {
      wordlists: this.fetchData(1, 25),
      wordlistsFields: [
        {key: 'name', sortable: true},
        {key: 'type', sortable: true},
        {key: 'size', sortable: true},
        {key: 'creator.username', label: 'Creator', sortable: true},
        {key: 'actions', sortable: false}
      ],
      selectedWordlist: null
    }
  },
  components: {
    DeleteConfirmation,
    WordlistForm,
    Pagination
  },
  methods: {
    fetchData (page = null, size = null) {
      WordlistApi.getAllWordlists(page, size).then(wordlists => { this.wordlists = wordlists })
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
          this.fetchData(this.page, this.size)
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
