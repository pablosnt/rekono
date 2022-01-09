<template>
  <div>
    <TableHeader :filters="filters" add="wordlist-modal" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="wordlistsFields" :items="wordlists">
      <template #cell(likes)="row">
        {{ row.item.likes }}
        <b-button variant="outline">
          <b-icon variant="danger" v-if="row.item.liked" icon="heart-fill" @click="dislike('resources/wordlists', row.item.id); fetchData()"/>
          <b-icon variant="danger" v-if="!row.item.liked" icon="heart" @click="like('resources/wordlists', row.item.id); fetchData()"/>
        </b-button>
      </template>
      <template #cell(actions)="row">
        <b-dropdown variant="outline" right>
          <template #button-content>
            <b-icon variant="dark" icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item variant="dark" @click="selectWordlist(row.item)" v-b-modal.wordlist-modal :disabled="$store.state.role !== 'Admin' && (!row.item.creator || $store.state.user !== row.item.creator.id)">
            <b-icon icon="pencil-square"/>
            <label class="ml-1">Edit</label>
          </b-dropdown-item>
          <b-dropdown-item variant="danger" @click="selectWordlist(row.item)" v-b-modal.delete-wordlist-modal :disabled="$store.state.role !== 'Admin' && (!row.item.creator || $store.state.user !== row.item.creator.id)">
            <b-icon icon="trash-fill"/>
            <label class="ml-1">Delete</label>
          </b-dropdown-item>
        </b-dropdown>
      </template>
    </b-table>
    <Pagination :page="page" :limit="limit" :limits="limits" :total="total" name="wordlists" @pagination="pagination"/>
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
import AlertMixin from '@/common/mixin/AlertMixin.vue'
import PaginationMixin from '@/common/mixin/PaginationMixin.vue'
import LikeMixin from '@/common/mixin/LikeMixin.vue'
import WordlistForm from '@/modals/WordlistForm.vue'
export default {
  name: 'wordlistsPage',
  mixins: [AlertMixin, PaginationMixin, LikeMixin],
  data () {
    return {
      wordlists: this.fetchData(),
      wordlistsFields: [
        { key: 'name', label: 'Wordlist', sortable: true },
        { key: 'type', sortable: true },
        { key: 'size', sortable: true },
        { key: 'creator.username', label: 'Creator', sortable: true },
        { key: 'likes', sortable: true },
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
    wordlists () {
      this.filters = [
        { name: 'Type', values: ['Endpoint', 'Password'], valueField: 'value', textField: 'value', filterField: 'type' },
        { name: 'Max. Size', filterField: 'size__lte', type: 'number' },
        { name: 'Creator', filterField: 'creator__username__icontains', type: 'text' },
        { name: 'Favourities', values: [{ value: true, text: 'True' }, { value: false, text: 'False' }], valueField: 'value', textField: 'text', filterField: 'liked' }
      ] 
    }
  },
  methods: {
    fetchData (filter = null) {
      WordlistApi.getPaginatedWordlists(this.getPage(), this.getLimit(), filter).then(data => {
        this.total = data.count
        this.wordlists = data.results
      })
    },
    deleteWordlist () {
      WordlistApi.deleteWordlist(this.selectedWordlist.id)
        .then(() => {
          this.$bvModal.hide('delete-wordlist-modal')
          this.warning(this.selectedWordlist.name, 'Wordlist deleted successfully')
          this.fetchData()
        })
        .catch(() => {
          this.danger(this.selectedWordlist.name, 'Unexpected error in wordlist deletion')
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
