import RekonoApi from "./api";

class Profile extends RekonoApi {
  getProfile () {
    return super.get('/api/profile/')
      .then(response => {
        return response.data
      })
  }

  updateProfile (firstName, lastName, notificationScope, emailNotification, telegramNotification) {
    let data = {
      first_name: firstName,
      last_name: lastName,
      notification_scope: notificationScope,
      email_notification: emailNotification,
      telegram_notification: telegramNotification
    }
    return super.put('/api/profile/', data)
      .then(response => {
        return response.data
      })
  }

  changePassword (password, oldPassword) {
    return super.put('/api/profile/change-password/', { password: password, old_password: oldPassword }, true, null, true)
      .then(response => {
        return response.data
      })
  }

  configureTelegram (telegramToken) {
    return super.post('/api/profile/telegram-token/', { token: telegramToken })
      .then(response => {
        return response.data
      })
  }

  getApiKey (username, password) {
    return super.post('/api/api-token/', { username: username, password: password })
      .then(response => {
        return response.data
      })
  }
}

export default new Profile()
