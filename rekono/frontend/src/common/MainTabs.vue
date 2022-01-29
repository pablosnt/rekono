<template>
  <b-tabs fill card vertical active-nav-item-class="font-weight-bold text-danger">
    <b-tab lazy :active="path.includes('dashboard')" @click="click('dashboard')" title-link-class="text-left text-secondary">
      <template #title>
        <b-icon icon="bar-chart-line-fill"/><span v-if="$store.state.mainTabs"> Dashboard</span>
      </template>
      <slot name="dashboard"/>
    </b-tab>
    <b-tab lazy :active="path.includes('projects')" @click="click('projects')" title-link-class="text-left text-secondary">
      <template #title>
        <b-icon icon="box"/><span v-if="$store.state.mainTabs"> Projects</span>
      </template>
      <slot name="projects"/>
    </b-tab>
    <b-tab lazy :active="path.includes('tools')" @click="click('tools')" v-if="auditor.includes($store.state.role)" title-link-class="text-left text-secondary">
      <template #title>
        <b-icon icon="gear-fill"/><span v-if="$store.state.mainTabs"> Tools</span>
      </template>
      <slot name="tools"/>
    </b-tab>
    <b-tab lazy :active="path.includes('processes')" @click="click('processes')" v-if="auditor.includes($store.state.role)" title-link-class="text-left text-secondary">
      <template #title>
        <b-icon icon="grid1x2-fill"/><span v-if="$store.state.mainTabs"> Processes</span>
      </template>
      <slot name="processes"/>
    </b-tab>
    <b-tab lazy :active="path.includes('wordlists')" @click="click('wordlists')" v-if="auditor.includes($store.state.role)" title-link-class="text-left text-secondary">
      <template #title>
        <b-icon icon="file-earmark-word-fill"/><span v-if="$store.state.mainTabs"> Wordlists</span>
      </template>
      <slot name="wordlists"/>
    </b-tab>
    <b-tab lazy :active="path.includes('users')" @click="click('users')" v-if="$store.state.role === 'Admin'" title-link-class="text-left text-secondary">
      <template #title>
        <b-icon icon="people-fill"/><span v-if="$store.state.mainTabs"> Users</span>
      </template>
      <slot name="users"/>
    </b-tab>
    <template #tabs-end>
      <b-button class="mt-5" variant="outline" @click="$store.dispatch('changeMainTabs')">
        <b-icon v-if="$store.state.mainTabs" icon="chevron-double-left"/>
        <b-icon v-if="!$store.state.mainTabs" icon="chevron-double-right"/>
      </b-button>
    </template>
  </b-tabs>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'mainTabs',
  mixins: [RekonoApi],
  data () {
    return {
      path: window.location.hash
    }
  },
  methods: {
    click (tab) {
      this.$emit('click', tab)
    }
  }
}
</script>
