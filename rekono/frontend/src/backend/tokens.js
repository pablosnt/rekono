import jwtDecode from 'jwt-decode'

const accessTokenKey = 'access-token'
const refreshTokenKey = 'refresh-token'

function removeTokens () {
  localStorage.removeItem(accessTokenKey)
  localStorage.removeItem(refreshTokenKey)
}

function decodeToken (accessToken) {
  const decoded = jwtDecode(accessToken)
  return {
    user: decoded.user_id,
    role: decoded.role
  }
}

function processTokens (tokens) {
  localStorage.setItem(accessTokenKey, tokens.access)
  localStorage.setItem(refreshTokenKey, tokens.refresh)
  return decodeToken(tokens.access)
}

export {
  accessTokenKey,
  refreshTokenKey,
  removeTokens,
  decodeToken,
  processTokens
}