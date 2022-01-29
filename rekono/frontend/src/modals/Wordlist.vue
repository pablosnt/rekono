<template>
  <b-modal :id="id" @hidden="clean" @ok="confirm" :title="title" :ok-title="button" header-bg-variant="dark" header-text-variant="light" ok-variant="dark">
    <b-form ref="wordlist_form">
      <b-form-group description="Name" invalid-feedback="Wordlist name is required">
        <b-form-input v-model="name" type="text" :state="nameState" maxlength="50" required/>
      </b-form-group>
      <b-form-group description="Type">
        <b-form-select v-model="type" :options="types" required/>
      </b-form-group>
      <b-form-group description="File" :invalid-feedback="fileInvalidFeedback">
        <b-form-file v-model="file" accept="text/plain" placeholder="Select the wordlist file" drop-placeholder="Drop the wordlist here" :state="fileState" required/>
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
      types: ['Endpoint', 'Password'],
      file: null,
      nameState: null,
      fileState: null,
      fileInvalidFeedback: 'Wordlist file is required',
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
      const valid = this.$refs.wordlist_form.checkValidity()
      this.nameState = (this.name !== null && this.name.length > 0)
      this.fileState = (this.file !== null)
      this.fileInvalidFeedback = 'Wordlist file is required'
      if (this.fileState && this.file.size / (1024 * 1024) > this.fileMaxSize) {
        this.fileState = false
        this.fileInvalidFeedback = "Wordlist file can't be grater than 500 MB"
      }
      return valid && this.fileState
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
        '/api/resources/wordlists/',
        this.getFormData(),
        this.name, 'New wordlist created successfully',
        false, { 'Content-Type': 'multipart/form-data' }
      )
    },
    update () {
      return this.put(
        `/api/resources/wordlists/${this.wordlist.id}/`,
        this.getFormData(),
        this.name, 'New wordlist created successfully',
        false, { 'Content-Type': 'multipart/form-data' }
      )
    },
    getFormData () {
      const data = new FormData()
      data.append('name', this.name)
      data.append('type', this.type)
      data.append('file', this.file)
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
