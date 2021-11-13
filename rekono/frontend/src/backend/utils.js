import store from '../store/'

const headers = () => {
  var base = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
  if (store.state.user) {
    var accessToken = localStorage['access_token']
    base['Authorization'] = 'Bearer ' + accessToken
  }
  return base
}

export {
  headers
}
