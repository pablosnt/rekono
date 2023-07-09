<template>
  <b-modal :id="id" :title="'Target ' + target.target" header-bg-variant="dark" header-text-variant="light" size="lg" hide-footer @hidden="close()">
    <b-tabs fill card active-nav-item-class="text-danger">
      <b-tab lazy title-link-class="text-secondary">
        <template #title>
          <b-icon icon="stack"/> Ports
        </template>
        <target-port :targetId="target.id"/>
      </b-tab>
      <b-tab lazy title-link-class="text-secondary">
        <template #title>
          <b-icon icon="cpu-fill"/> Technologies
        </template>
        <technology :targetId="target.id"/>
      </b-tab>
      <b-tab lazy title-link-class="text-secondary">
        <template #title>
          <b-icon icon="bug-fill"/> Vulnerabilities
        </template>
        <vulnerability :targetId="target.id"/>
      </b-tab>
    </b-tabs>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi';
import TargetPort from '@/modals/targets/TargetPort';
import Technology from '@/modals/targets/Technology';
import Vulnerability from '@/modals/targets/Vulnerability';
export default {
  name: 'targetDetailsModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    target: Object
  },
  components: {
    TargetPort,
    Technology,
    Vulnerability,
  },
  methods: {
    close () {
      this.$emit('close')
    }
  }
}
</script>