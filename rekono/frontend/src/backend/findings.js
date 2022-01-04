import RekonoApi from './api'

class Finding extends RekonoApi {
  getAllFindings (path, filter = null) {
    return super.getAllPages(`/api/${path}/?o=-creation`, filter)
  }
}

export default new Finding()
