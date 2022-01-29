<template>
  <div>
    <b-row class="mb-2">
      <b-col :cols="filterCols">
        <b-input-group>
          <b-input-group-prepend>
            <b-button variant="danger" @click="filter"><b-icon icon="search"/></b-button>
          </b-input-group-prepend>
          <b-form-input v-model="searchInput" placeholder="Search" type="search" @input="filter"/>
        </b-input-group>
      </b-col>
      <b-col v-if="(add && addIcon && showAdd === true) || (filters && filters.length > 0)">
        <div class="text-right">
          <b-button id="filter-button" v-if="filters && filters.length > 0" variant="outline" v-b-toggle.filters @click="toggleFilters()">
            <p class="h3">
              <b-icon v-if="!showFilters" icon="filter-square-fill"/>
              <b-icon v-if="showFilters" icon="dash-circle-fill"/>
            </p>
          </b-button>
          <b-tooltip target="filter-button" triggers="hover" title="Filter" v-if="showFilters && filters && filters.length > 0"/>
          <b-tooltip target="filter-button" triggers="hover" title="Clean Filter" v-if="!showFilters && filters && filters.length > 0"/>
          <span/>
          <b-button v-if="add && addIcon && showAdd === true" variant="outline" @click="$emit('add-click')" v-b-tooltip.hover title="Add" v-b-modal="add">
            <p class="h3"><b-icon variant="success" :icon="addIcon"/></p>
          </b-button>
        </div>
      </b-col>
    </b-row>
    <b-collapse id="filters">
      <b-row class="mb-2">
        <b-col v-for="ft in filters" :key="ft.name">
          <b-form-group :description="ft.name">
            <b-form-tags no-outer-focus v-if="!ft.values && ft.type === 'tags'" placeholder="" remove-on-delete size="md" tag-variant="dark" @input="filter(ft.filterField, $event)"/>
            <b-form-input v-if="!ft.values && ft.type !== 'tags'" :type="ft.type" @input="filter(ft.filterField, $event)"/>
            <b-form-select v-if="ft.values" :value="ft.default" :options="ft.values" :value-field="ft.valueField" :text-field="ft.textField" @change="filter(ft.filterField, $event)">
              <template #first>
                <b-form-select-option :value="null">Select {{ ft.name.toLowerCase() }}</b-form-select-option>
              </template>
            </b-form-select>
          </b-form-group>
        </b-col>
      </b-row>
    </b-collapse>
  </div>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'tableHeader',
  mixins: [RekonoApi],
  props: {
    filters: Array,
    add: String,
    showAdd: {
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
      return (this.showAdd === true || (this.filters && this.filters.length > 0)) ? 8 : 12
    },
  },
  data () {
    return {
      showFilters: false,
      searchInput: null,
      selectedFilters: {}
    }
  },
  methods: {
    toggleFilters () {
      this.showFilters = !this.showFilters
      if (!this.showFilters) {
        this.clean()
      }
    },
    clean () {
      this.selectedFilters = {}
      this.filter()
    },
    filter (field = null, value = null) {
      if (field) {
        if (Array.isArray(value)) {
          value = value.join(',')
        }
        this.selectedFilters[field] = value
      }
      this.$emit('filter', Object.assign({}, this.selectedFilters, { search: this.searchInput }))
    }
  }
}
</script>
