<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" :title="title" :ok-title="button" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="wordlist_form">
      <b-form-group description="Name" :invalid-feedback="invalidName">
        <b-form-input v-model="name" type="text" :state="nameState" maxlength="50"/>
      </b-form-group>
      <b-form-group description="Type">
        <b-form-select v-model="type" :options="wordlistTypes"/>
      </b-form-group>
      <b-form-group description="File" :invalid-feedback="invalidFile" v-if="!edit">
        <b-form-file v-model="file" accept="text/plain" placeholder="Select the wordlist file" drop-placeholder="Drop the wordlist here" :state="fileState"/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import RekonoApi from '@/backend/RekonoApi'
export default {
  name: 'wordlistModal',
  mixins: [RekonoApi],
  props: {
    id: String,
    wordlist: Object,
    initialized: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    edit () {
      return (this.wordlist !== null)
    },
    title () {
      return this.wordlist !== null ? 'Edit Wordlist' : 'New Wordlist'
    },
    button () {
      return this.wordlist !== null ? 'Update Wordlist' : 'Create Wordlist'
    }
  },
  data () {
    return {
      name: null,
      type: 'Endpoint',
      file: null,
      nameState: null,
      fileState: null,
      invalidName: 'Wordlist name is required',
      invalidFile: 'Wordlist file is required',
      fileMaxSize: 500
    }
  },
  watch: {
    wordlist (wordlist) {
      if (this.initialized && wordlist !== null) {
        this.name = wordlist.name
        this.type = wordlist.type
      }
    }
  },
  methods: {
    check () {
      if (!this.validateName(this.name)) {
        this.nameState = false
        this.invalidName = this.name && this.name.length > 0 ? 'Invalid wordlist name' : 'Wordlist name is required'
      }
      if (!this.edit) {
        this.fileState = (this.file !== null)
        this.invalidFile = 'Wordlist file is required'
        if (this.fileState && this.file.size / (1024 * 1024) > this.fileMaxSize) {
          this.fileState = false
          this.invalidFile = "Wordlist file can't be grater than 500 MB"
        }
      }
      return this.nameState !== false && this.fileState !== false
    },
    confirm (event) {
      event.preventDefault()
      if (this.check()) {
        const operation = this.edit ? this.update() : this.create()
        operation
          .then(() => { return Promise.resolve(true) })
          .catch(() => { return Promise.resolve(false) })
          .then(success => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    create () {
      return this.post(
        '/api/wordlists/',
        this.getFormData(),
        this.name, 'New wordlist created successfully',
        true, { 'Content-Type': 'multipart/form-data' }
      )
    },
    update () {
      return this.put(`/api/wordlists/${this.wordlist.id}/`, { 'name': this.name, 'type': this.type }, this.name, 'Wordlist updated successfully')
    },
    getFormData () {
      const data = new FormData()
      data.append('name', this.name)
      data.append('type', this.type)
      data.append('file', this.file)
      return data
    },
    clean () {
      this.name = null
      this.type = 'Endpoint'
      this.file = null
      this.nameState = null
      this.fileState = null
      this.$emit('clean')
    }
  }
}
</script>
