export function useApi(endpoint: string, authentication: boolean = true, refreshData: boolean = true, refreshAll: boolean = false, entity?: string, extraHeaders?: object) {
    const config = useRuntimeConfig()
    const router = useRouter()
    const refreshing = refreshStore()
    const alert = useAlert()
    const tokens = useTokens()
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
        Accept: 'application/json'
    }

    const default_size = 25
    const max_size = 1000
    let total = 0
    let items = []

    function url(endpoint: string): string {
        const currentEndpoint = config.backendRootPath ? config.backendRootPath + endpoint : endpoint
        if (config.backendUrl) {
            var url = new URL(config.backendUrl)
            url.pathname = currentEndpoint
            return url.href
        }
        return currentEndpoint
    }

    function headers(authentication: boolean): object {
        let currentHeaders = defaultHeaders
        const token = tokens.get().access
        if (authentication && token) {
            currentHeaders.Authorization = `Bearer ${token}`
        }
        return Object.assign({}, currentHeaders, extraHeaders)
    }

    function request(endpoint: string, options = {}): Promise<any> {
        return $fetch(url(endpoint), options)
            .catch((error) => {
                let message = 'Unexpected error'
                switch (error.statusCode) {
                    case 400:
                        const value = Object.values(error.data)[0][0]
                        const field = Object.keys(error.data)[0]
                        const body = `${value.charAt(0).toUpperCase()}${value.slice(1)}`
                        message = field !== 'non_field_errors' ? `${field}: ${body}` : body
                        break
                    case 401:
                        if (endpoint === '/api/security/refresh/') {
                            message = null
                        } else if (authentication) {
                            return refresh()
                                .then(() => {
                                    options.headers = headers(authentication)
                                    return request(endpoint, options)
                                })
                                .catch(() => { return router.push({ name: 'login' }) })
                        } else {
                            message = 'Invalid credentials'
                        }
                        break
                    case 403:
                        message = 'You are not authorized to perform this operation'
                        break
                    case 404:
                        message = 'Resource not found'
                        break
                    case 429:
                        message = 'Too many requests'
                        break
                }
                if (message) {
                    alert(message, 'error')
                }
                return Promise.reject(error)
            })
    }

    function refresh(): Promise<any> {
        if (!refreshing.refreshing) {
            refreshing.change()
            return request('/api/security/refresh/', { method: 'POST', headers: headers(true), body: { refresh: tokens.get().refresh }})
                .then((response) => {
                    tokens.remove()
                    tokens.save(response)
                    refreshing.change()
                    return Promise.resolve()
                })
                .catch((error) => {
                    tokens.remove()
                    refreshing.change()
                    return Promise.reject()
                })
        }
        else {
            while (refreshing.refreshing) {}
            return Promise.resolve()
        }
    }

    function get(id?: number): Promise<any> {
        return request(id ? `${endpoint}${id}/` : endpoint, { method: 'GET', headers: headers(authentication) })
            .then((response) => {
                return Promise.resolve(response)
            })
    }

    function list(params = {}, all = false, page = 1): Promise<any> {
        const size = all ? max_size : default_size
        if (page === 1 && all) {
            items = []
        }
        return request(endpoint, { method: 'GET', headers: headers(authentication), params: Object.assign({}, params, { page: page, size: size }) })
            .then((response) => {
                total = response.count
                if (all) {
                    items = items.concat(response.results)
                    if ((page * size) < total) {
                        return list(params, all, page + 1)
                    }
                } else {
                    items = response.results
                }
                return Promise.resolve({ items: items, total: total })
            })
    }

    function create(body: object) {
        return request(endpoint, { method: 'POST', headers: headers(authentication), body: body })
            .then((response) => {
                if (response) {
                    if (items && refreshData) {
                        return list(refreshAll)
                    }
                    if (entity) {
                        alert(`New ${entity.toLowerCase()} has been successfully created`, 'success')
                    }
                }
                return Promise.resolve(response)
            })
    }

    function update(body: object, id?: number) {
        return request(id ? `${endpoint}${id}/` : endpoint, { method: 'PUT', headers: headers(authentication), body: body })
            .then((response) => {
                if (response) {
                    if (refreshData && items) {
                        return list(refreshAll)
                    }
                    if (entity) {
                        alert(`${entity} has been successfully updated`, 'success')
                    }
                }
                return Promise.resolve(response)
            })
    }

    function remove(id?: number) {
        return request(id ? `${endpoint}${id}/` : endpoint, { method: 'DELETE', headers: headers(authentication) })
            .then((response) => {
                if (response) {
                    if (refreshData && items) {
                        return list(refreshAll)
                    }
                    if (entity) {
                        alert(`${entity} has been deleted`, 'warning')
                    }
                }
                return Promise.resolve(response)
            })
    }

    return { get, list, create, update, remove, default_size }
}