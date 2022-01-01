<template>
  <b-card fluid>
    <b-tabs fill card vertical active-nav-item-class="font-weight-bold text-danger">
      <b-tab lazy active @click="click('dashboard')" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="bar-chart-line-fill"/> Dashboard
        </template>
        <slot name="dashboard"/>
      </b-tab>
      <b-tab lazy :active="path.includes('projects')" @click="click('projects')" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="box"/> Projects
        </template>
        <slot name="projects"/>
      </b-tab>
      <b-tab lazy :active="path.includes('tools')" @click="click('tools')" v-if="auditor.includes($store.state.role)" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="gear-fill"/> Tools
        </template>
        <slot name="tools"/>
      </b-tab>
      <b-tab lazy :active="path.includes('processes')" @click="click('processes')" v-if="auditor.includes($store.state.role)" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="grid1x2-fill"/> Processes
        </template>
        <slot name="processes"/>
      </b-tab>
      <b-tab lazy :active="path.includes('wordlists')" @click="click('wordlists')" v-if="auditor.includes($store.state.role)" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="chat-left-dots-fill"/> Wordlists
        </template>
        <slot name="wordlists"/>
      </b-tab>
      <b-tab lazy :active="path.includes('users')" @click="click('users')" v-if="$store.state.role === 'Admin'" title-link-class="text-left text-secondary">
        <template #title>
          <b-icon icon="person-fill"/> Users
        </template>
        <slot name="users"/>
      </b-tab>
    </b-tabs>
  </b-card>
</template>

<script>
import { auditor } from '@/backend/constants'
export default {
  name: 'projectDetails',
  data () {
    return {
      auditor: auditor,
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
