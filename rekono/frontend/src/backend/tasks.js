import RekonoApi from './api'

class Task extends RekonoApi {
  getPaginatedTasks (page = null, limit = null, filter = null) {
    return super.get('/api/tasks/', page, limit, filter)
      .then(response => {
        return response.data
      })
  }

  getTask (taskId) {
    return super.get(`/api/tasks/${taskId}/`)
      .then(response => {
        return response.data
      })
  }

  repeatTask (taskId) {
    return super.post(`/api/tasks/${taskId}/repeat/`, { })
      .then(response => {
        return response.data
      })
  }

  createTask (target, process, tool, configuration, intensity, scheduledAtDate, scheduledAtTime, scheduledIn, scheduledTimeUnit, repeatIn, repeatTimeUnit, wordlists) {
    const data = {
      target_id: target,
      intensity_rank: intensity,
      scheduled_at: scheduledAtDate !== null && scheduledAtTime !== null ? `${scheduledAtDate}T${scheduledAtTime}Z` : null,
      scheduled_in: scheduledIn,
      schduled_time_unit: scheduledTimeUnit,
      repeat_in: repeatIn,
      repeat_time_unit: repeatTimeUnit,
      wordlists: wordlists
    }
    if (process) {
      data.process_id = process
    }
    if (tool) {
      data.tool_id = tool
    }
    if (configuration) {
      data.configuration_id = configuration
    }
    return super.post('/api/tasks/', data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  cancelTask (taskId) {
    return super.delete(`/api/tasks/${taskId}/`)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  countTasks (filter = null) {
    return super.get('/api/tasks/', 1, 1, filter)
      .then(response => {
        return response.data.count
      })
  }
}

export default new Task()
