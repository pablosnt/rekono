import { rekonoApiPost } from './api'

const createTask = (target, process, tool, configuration, intensity, scheduledAtDate, scheduledAtTime, scheduledIn, scheduledTimeUnit, repeatIn, repeatTimeUnit, wordlists) => {
  var data = {
    target: target,
    process: process,
    tool: tool,
    configuration: configuration,
    intensity_rank: intensity,
    scheduled_at: scheduledAtDate !== null && scheduledAtTime !== null ? scheduledAtDate + 'T' + scheduledAtTime + 'Z' : null,
    scheduled_in: scheduledIn,
    schduled_time_unit: scheduledTimeUnit,
    repeat_in: repeatIn,
    repeat_time_unit: repeatTimeUnit,
    wordlists: wordlists
  }
  return rekonoApiPost('/api/tasks/', data)
    .then(response => {
      return Promise.resolve(response.data)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export { createTask }
