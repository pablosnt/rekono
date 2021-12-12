<template>
  <b-row v-if="total > sizesItems[0]">
    <b-col cols="6">
      <b-pagination v-model="selectedPage" :total-rows="total" :per-page="size" align="right" first-class="text-black" ellipsis-class="text-black" last-class="text-black" next-class="text-black" prev-class="text-black">
        <template #page="{ page, active }">
          <b v-if="active" class="text-light">{{ page }}</b>
          <i v-else class="text-dark">{{ page }}</i>
        </template>
      </b-pagination>
    </b-col>
    <b-col cols="2">
      <b-form-select v-model="selectedSize" :options="sizesItems">
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
  props: ['name', 'page', 'size', 'sizes', 'total'],
  computed: {
    sizesItems () {
      if (this.total > 0) {
        var items = []
        for (var s = 0; s < this.sizes.length; s++) {
          if (this.sizes[s] < this.total) {
            items.push(this.sizes[s])
          }
        }
        return items
      } else {
        return this.sizes
      }
    }
  },
  data () {
    return {
      selectedPage: this.page,
      selectedSize: this.size
    }
  },
  watch: {
    page (page) {
      this.selectedPage = page
    },
    size (size) {
      if (size > this.total) {
        this.selectedSize = this.total
      } else {
        this.selectedSize = size
      }
    },
    sizesItems (sizes) {
      if (!sizes.includes(this.size)) {
        if (this.size > this.total) this.selectedSize = this.total
        else this.selectedSize = sizes[0]
      }
    },
    selectedPage (page) {
      this.$emit('pagination', { page: page, size: this.selectedSize })
    },
    selectedSize (size) {
      this.$emit('pagination', { page: this.selectedPage, size: size })
    }
  }
}
</script>
