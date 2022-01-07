import RekonoApi from './api'

class Like extends RekonoApi {
  like (path, id) {
    return super.post(`/api/${path}/${id}/like/`, { })
  }

  dislike (path, id) {
    return super.post(`/api/${path}/${id}/dislike/`, { })
  }
}

export default new Like()
