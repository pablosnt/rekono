<template>
  <b-row v-if="total > limitItems[0]">
    <b-col cols="6">
      <b-pagination v-model="selectedPage" :total-rows="total" :per-page="limit" align="right" first-class="text-black" ellipsis-class="text-black" last-class="text-black" next-class="text-black" prev-class="text-black">
        <template #page="{ page, active }">
          <strong v-if="active" class="text-light">{{ page }}</strong>
          <em v-else class="text-dark">{{ page }}</em>
        </template>
      </b-pagination>
    </b-col>
    <b-col cols="2">
      <b-form-select v-model="selectedLimit" :options="limitItems">
        <template #first>
          <b-form-select-option :value="total">All {{ name }}</b-form-select-option>
        </template>
      </b-form-select>
    </b-col>
  </b-row>
</template>

<script>
export default {
  name: 'pagination',
  props: ['name', 'page', 'limit', 'limits', 'total'],
  computed: {
    limitItems () {
      if (this.total > 0) {
        let items = this.limits.filter(limit => limit < this.total)
        if (items.length === 0) {
          items = [this.limits[0]]
        }
        return items
      } else {
        return this.limits
      }
    }
  },
  data () {
    return {
      selectedPage: this.page,
      selectedLimit: this.limit
    }
  },
  watch: {
    page (page) {
      this.selectedPage = page
    },
    limit (limit) {
      this.selectedLimit = limit
    },
    selectedPage (page) {
      this.$emit('pagination', { page: page, limit: this.selectedLimit })
    },
    selectedLimit (limit) {
      this.$emit('pagination', { page: this.selectedPage, limit: limit })
    }
  }
}
</script>
