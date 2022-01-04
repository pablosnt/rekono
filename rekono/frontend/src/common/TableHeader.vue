<template>
  <div>
    <b-row class="mb-2">
      <b-col :cols="filterCols">
        <b-input-group>
          <b-input-group-prepend>
            <b-button variant="danger" @click="filter"><b-icon icon="search"/></b-button>
          </b-input-group-prepend>
          <b-form-input v-model="searchInput" placeholder="Search" type="search" @change="filter"/>
        </b-input-group>
      </b-col>
      <b-col v-if="(add && addIcon && addAuth === true) || (filters && filters.length > 0)">
        <div class="text-right">
          <b-button v-if="filters && filters.length > 0 && !showFilters" variant="outline" v-b-tooltip.hover title="Filter" @click="toggleFilters()">
            <p class="h3"><b-icon icon="filter-square-fill"/></p>
          </b-button>
          <b-button v-if="filters && filters.length > 0 && showFilters" variant="outline" v-b-tooltip.hover title="Clean Filter" @click="clean()">
            <p class="h3"><b-icon icon="dash-circle-fill"/></p>
          </b-button>
          <span/>
          <b-button v-if="add && addIcon && addAuth === true" variant="outline" @click="$emit('add-click')" v-b-tooltip.hover title="Add" v-b-modal="add">
            <p class="h3"><b-icon variant="success" :icon="addIcon"/></p>
          </b-button>
        </div>
      </b-col>
    </b-row>
    <b-row v-if="showFilters" class="mb-2">
      <b-col v-for="ft in filters" :key="ft.name">
        <b-form-group :description="ft.name">
          <b-form-input :id="ft.filterField" v-if="!ft.values" :type="ft.type" @change="filter"/>
          <b-form-select :id="ft.filterField" v-if="ft.values" :value="ft.default" :options="ft.values" :value-field="ft.valueField" :text-field="ft.textField" @change="filter">
            <template #first>
              <b-form-select-option :value="null">Select {{ ft.name.toLowerCase() }}</b-form-select-option>
            </template>
          </b-form-select>
        </b-form-group>
      </b-col>
    </b-row>
  </div>
</template>

<script>
export default {
  name: 'tableHeader',
  props: {
    filters: {
      type: Array,
      default: null
    },
    add: {
      type: String,
      default: null
    },
    addAuth: {
      type: Boolean,
      default: true
    },
    addIcon: {
      type: String,
      default: 'plus-square-fill'
    }
  },
  computed: {
    filterCols () {
      return (this.addAuth === true || (this.filters && this.filters.length > 0)) ? 8 : 12
    },
    selectedFilters () {
      let data = {}
      data.search = this.searchInput
      if (this.filters) {
        for (let i=0; i < this.filters.length; i++) {
          const input = document.getElementById(this.filters[i].filterField)
          if (input && input.value && input.value.length > 0) {
            data[this.filters[i].filterField] = input.value
          }
        }
      }
      return data
    }
  },
  data () {
    return {
      showFilters: false,
      searchInput: null
    }
  },
  methods: {
    toggleFilters () {
      this.showFilters = !this.showFilters
    },
    clean () {
      this.toggleFilters()
      for (let i=0; i < this.filters.length; i++) {
        const input = document.getElementById(this.filters[i].filterField)
        if (input) {
          input.value = null
        }
      }
      this.filter()
    },
    filter () {
      this.$emit('filter', this.selectedFilters)
    }
  }
}
</script>
