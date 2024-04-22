export const refreshStore = defineStore('refresh', {
  state: () => ({ refreshing: false }),
  actions: {
    change() {
      refreshing = !refreshing
    }
  }
})
