export const refreshStore = defineStore('refresh', {
  state: () => ({ refreshing: false }),
  actions: {
    change() {
      this.refreshing = !this.refreshing
    }
  }
})
