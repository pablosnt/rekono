<template>
  <b-modal :id="id" @hidden="cancel" @ok="confirm" :title="edit ? 'Edit Process' : 'New Process'" :ok-title="edit ? 'Update Process' : 'Create Process'">
    <b-form ref="process_form">
      <b-form-group description="Process name" invalid-feedback="Process name is required">
        <b-form-input v-model="name" type="text" :state="nameState" maxlength="30" required/>
      </b-form-group>
      <b-form-group invalid-feedback="Process description is required">
        <b-form-textarea v-model="description" placeholder="Process description" :state="descriptionState" maxlength="350" required/>
      </b-form-group>
    </b-form>
  </b-modal>
</template>

<script>
import { createProcess, updateProcess } from '../../backend/processes'
export default {
  name: 'processForm',
  props: ['id', 'process'],
  computed: {
    edit () {
      return (this.process !== null)
    }
  },
  data () {
    return {
      name: null,
      description: null,
      nameState: null,
      descriptionState: null
    }
  },
  watch: {
    process (process) {
      if (process !== null) {
        this.name = process.name
        this.description = process.description
      }
    }
  },
  methods: {
    check () {
      const valid = this.$refs.process_form.checkValidity()
      this.nameState = (this.description !== null && this.description.length > 0)
      this.descriptionState = (this.name !== null && this.name.length > 0)
      return valid
    },
    confirm (event) {
      event.preventDefault()
      if (!this.check()) {
        return
      }
      var operation = this.edit ? this.update() : this.create()
      operation.then((success) => this.$emit('confirm', { id: this.id, success: success }))
    },
    create () {
      return createProcess(this.name, this.description)
        .then(() => {
          this.$bvToast.toast('New process created successfully', {
            title: this.name,
            variant: 'success',
            solid: true
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in process creation', {
            title: this.name,
            variant: 'danger',
            solid: true
          })
          return Promise.resolve(false)
        })
    },
    update () {
      return updateProcess(this.process.id, this.name, this.description)
        .then(() => {
          this.$bvToast.toast('Process updated successfully', {
            title: this.name,
            variant: 'success',
            solid: true
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$bvToast.toast('Unexpected error in process update', {
            title: this.name,
            variant: 'danger',
            solid: true
          })
          return Promise.resolve(false)
        })
    },
    cancel () {
      this.name = null
      this.description = null
      this.nameState = null
      this.descriptionState = null
      this.$emit('cancel')
    }
  }
}
</script>
