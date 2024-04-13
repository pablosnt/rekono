import { defineStore } from 'pinia'

export const refreshStore = defineStore('refresh', {
  state: () => ({ refreshing: false }),
  actions: {
    change() {
      refreshing = !refreshing
    }
  }
})
