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

const headers = (requiredAuth = true, extra = null) => {
  var requestHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
  if (store.state.user && requiredAuth) {
    var accessToken = localStorage[accessTokenKey]
    requestHeaders['Authorization'] = 'Bearer ' + accessToken
  }
  if (extra !== null) {
    requestHeaders = Object.assign({}, requestHeaders, extra)
  }
  return requestHeaders
}

const findById = (data, id) => {
  for (var i = 0; i < data.length; i++) {
    if (data[i].id === id) {
      return data[i]
    }
  }
  return null
}

export {
  accessTokenKey, refreshTokenKey, decodeToken, headers, findById
}
