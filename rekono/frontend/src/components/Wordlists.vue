<template>
  <div>
    <table-header :filters="filters" add="wordlist-modal" @filter="fetchData"/>
    <b-table striped borderless head-variant="dark" :fields="wordlistsFields" :items="data">
      <template #cell(likes)="row">
        {{ row.item.likes }}
        <b-button variant="outline">
          <b-icon variant="danger" v-if="row.item.liked" icon="heart-fill" @click="dislikeWordlist(row.item.id)"/>
          <b-icon variant="danger" v-if="!row.item.liked" icon="heart" @click="likeWordlist(row.item.id)"/>
        </b-button>
      </template>
      <template #cell(actions)="row">
        <b-dropdown variant="outline" right>
          <template #button-content>
            <b-icon variant="dark" icon="three-dots-vertical"/>
          </template>
          <b-dropdown-item variant="dark" @click="selectedWordlist = row.item" v-b-modal.wordlist-modal :disabled="$store.state.role !== 'Admin' && (!row.item.creator || $store.state.user !== row.item.creator.id)">
            <b-icon icon="pencil-square"/>
            <label class="ml-1">Edit</label>
          </b-dropdown-item>
          <b-dropdown-item variant="danger" @click="selectedWordlist = row.item" v-b-modal.delete-wordlist-modal :disabled="$store.state.role !== 'Admin' && (!row.item.creator || $store.state.user !== row.item.creator.id)">
            <b-icon icon="trash-fill"/>
            <label class="ml-1">Delete</label>
          </b-dropdown-item>
        </b-dropdown>
      </template>
    </b-table>
    <pagination :page="page" :limit="limit" :limits="limits" :total="total" name="wordlists" @pagination="pagination"/>
    <deletion id="delete-wordlist-modal" title="Delete Wordlist" @deletion="deleteWordlist" @clean="selectedWordlist = null" v-if="selectedWordlist !== null && selectedWordlist !== null">
      <span><strong>{{ this.selectedWordlist.name }}</strong> wordlist</span>
    </deletion>
    <wordlist id="wordlist-modal" :wordlist="selectedWordlist" :initialized="selectedWordlist !== null" @confirm="confirm" @clean="selectedWordlist = null"/>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
import Deletion from '@/common/Deletion'
import Pagination from '@/common/Pagination'
import TableHeader from '@/common/TableHeader'
import Wordlist from '@/modals/Wordlist'
export default {
  name: 'wordlistsPage',
  mixins: [RekonoApi],
  data () {
    this.fetchData()
    return {
      data: [],
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
    Wordlist
  },
  watch: {
    data () {
      this.filters = [
        { name: 'Type', values: ['Endpoint', 'Subdomain'], valueField: 'value', textField: 'value', filterField: 'type' },
        { name: 'Max Size', filterField: 'size__lte', type: 'number' },
        { name: 'Creator', filterField: 'creator__username__icontains', type: 'text' },
        { name: 'Favourities', type: 'checkbox', filterField: 'liked' }
      ] 
    }
  },
  methods: {
    fetchData (params = {}) {
      params.o = 'type,name'
      return this.getOnePage('/api/wordlists/', params)
        .then(response => {
          this.data = response.data.results
          this.total = response.data.count
        })
    },
    deleteWordlist () {
      this.delete(`/api/wordlists/${this.selectedWordlist.id}/`, this.selectedWordlist.name, 'Wordlist deleted successfully').then(() => this.fetchData())
    },
    likeWordlist (wordlistId) {
      this.post(`/api/wordlists/${wordlistId}/like/`, { }).then(() => this.fetchData())
    },
    dislikeWordlist (wordlistId) {
      this.post(`/api/wordlists/${wordlistId}/dislike/`, { }).then(() => this.fetchData())
    }
  }
}
</script>
