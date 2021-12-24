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
import WordlistApi from '@/backend/resources'
import NotificationMixin from '@/common/mixin/NotificationMixin.vue'
export default {
  name: 'wordlistForm',
  mixins: [NotificationMixin],
  initialized: {
    type: Boolean,
    default: false
  },
  props: {
    id: String,
    wordlist: {
      type: Object,
      default: null
    }
  },
  computed: {
    edit () {
      return (this.wordlist !== null)
    },
    title () {
      if (this.wordlist !== null) {
        return 'Edit Wordlist'
      } else {
        return 'New Wordlist'
      }
    },
    button () {
      if (this.wordlist !== null) {
        return 'Update Wordlist'
      } else {
        return 'Create Wordlist'
      }
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
        operation.then((success) => this.$emit('confirm', { id: this.id, success: success, reload: true }))
      }
    },
    create () {
      return WordlistApi.createWordlist(this.name, this.type, this.file)
        .then(() => {
          this.success(this.name, 'New wordlist created successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.name, 'Unexpected error in wordlist creation')
          return Promise.resolve(false)
        })
    },
    update () {
      return WordlistApi.updateWordlist(this.wordlist.id, this.name, this.type, this.file)
        .then(() => {
          this.success(this.name, 'New wordlist updated successfully')
          return Promise.resolve(true)
        })
        .catch(() => {
          this.danger(this.name, 'Unexpected error in wordlist update')
          return Promise.resolve(false)
        })
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
