<template>
  <b-modal :id="id" :title="'Target Port ' + targetPort.port" header-bg-variant="dark" header-text-variant="light" size="lg" hide-footer @hidden="close()">
    <b-tabs fill card active-nav-item-class="text-danger">
      <b-tab title-link-class="text-secondary">
        <template #title>
          <b-icon icon="shield-lock-fill"/> Authentication
        </template>
        <target-port-detail :targetPortId="targetPort.id" endpoint="authentications" name="authentication" field="name" :fields="targetAuthenticationFields"/>
      </b-tab>
      <b-tab title-link-class="text-secondary">
        <template #title>
          <b-icon icon="cpu-fill"/> Technologies
        </template>
        <target-port-detail :targetPortId="targetPort.id" endpoint="target-technologies" name="technology" field="name" :fields="targetTechnologiesFields"/>
      </b-tab>
      <b-tab title-link-class="text-secondary">
        <template #title>
          <b-icon icon="bug-fill"/> Vulnerabilities
        </template>
        <target-port-detail :targetPortId="targetPort.id" endpoint="target-vulnerabilities" name="vulnerability" field="cve" :fields="targetVulnerabilitiesFields"/>
      </b-tab>
    </b-tabs>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi';
import TargetPortDetail from '@/common/TargetPortDetail';
export default {
  name: 'targetPortModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    targetPort: Object
  },
  data () {
    return {
      targetAuthenticationFields: [
        { key: 'name' },
        { key: 'credential', label: 'Secret' },
        { key: 'type' }
      ],
      targetTechnologiesFields: [
        { key: 'name', label: 'Technology' },
        { key: 'version' }
      ],
      targetVulnerabilitiesFields: [
        { key: 'cve', label: 'CVE' }
      ]
    }
  },
  components: {
    TargetPortDetail
  },
  methods: {
    close () {
      this.$emit('close')
    }
  }
}
</script>