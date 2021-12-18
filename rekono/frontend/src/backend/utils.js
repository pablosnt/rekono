const accessTokenKey = 'access-token'
const refreshTokenKey = 'refresh-token'

const findById = (data, id) => {
  for (let i = 0; i < data.length; i++) {
    if (data[i].id === id) {
      return data[i]
    }
  }
  return null
}

export {
  accessTokenKey, refreshTokenKey, findById
}
