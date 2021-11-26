import store from '../store/'
import jwtDecode from 'jwt-decode'

const accessTokenKey = 'access-token'
const refreshTokenKey = 'refresh-token'

const decodeToken = (accessToken) => {
  var decoded = jwtDecode(accessToken)
  return {
    user: decoded.user_id,
    role: decoded.role
  }
}

const headers = () => {
  var base = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
  if (store.state.user) {
    var accessToken = localStorage[accessTokenKey]
    base['Authorization'] = 'Bearer ' + accessToken
  }
  return base
}

export {
  accessTokenKey, refreshTokenKey, decodeToken, headers
}
