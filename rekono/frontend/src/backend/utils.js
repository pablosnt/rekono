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

const headers = (requiredAuth = true) => {
  var requestHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
  if (store.state.user && requiredAuth) {
    var accessToken = localStorage[accessTokenKey]
    requestHeaders['Authorization'] = 'Bearer ' + accessToken
  }
  return requestHeaders
}

export {
  accessTokenKey, refreshTokenKey, decodeToken, headers
}
