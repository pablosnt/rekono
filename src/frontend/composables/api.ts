export function useApi(endpoint: string, authentication: boolean = true, refreshData: boolean = true, refreshAll: boolean = false, entity?: string, extraHeaders?: object) {
    const config = useRuntimeConfig()
    const router = useRouter()
    const refreshing = refreshStore()
    const alert = useAlert()
    const { getTokens, saveTokens, removeTokens } = useTokens()
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
        Accept: 'application/json'
    }
    // TODO: Separate pagination, it must be provided by the parent item
    let { page, limit, total, limits, max_limit } = usePagination()

    let data = ref({})
    let items = ref([])

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
        const token = getTokens().access
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
            return request('/api/security/refresh/', { method: 'POST', headers: headers(true), body: { refresh: getTokens().refresh }})
                .then((response) => {
                    removeTokens()
                    saveTokens(response)
                    refreshing.change()
                    return Promise.resolve()
                })
                .catch((error) => {
                    removeTokens()
                    refreshing.change()
                    return Promise.reject()
                })
        }
        else {
            console.log('WAITING')
            while (refreshing.refreshing) {}
            console.log('REPEAT')
            return Promise.resolve()
        }
    }

    function get(id?: number): Promise<any> {
        return request(id ? `${endpoint}${id}/` : endpoint, { method: 'GET', headers: headers(authentication) })
            .then((response) => {
                data = response
                return Promise.resolve(response)
            })
    }

    function list(params = {}, all = false, currentPage = 1): Promise<any> {
        const currentLimit = all ? max_limit : limit
        currentPage = all ? currentPage : page
        if (currentPage === 1 && all) {
            items = []
        }
        return request(endpoint, { method: 'GET', headers: headers(authentication), params: Object.assign({}, params, { page: currentPage, limit: currentLimit }) })
            .then((response) => {
                total = response.count
                items = items.concat(response.results)
                if ((currentPage * currentLimit) < total && all) {
                    return list(params, all, currentPage + 1)
                } else {
                    return Promise.resolve(items)
                }
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
                    if (refreshData) {
                        if (data) {
                            data = response
                        }
                        if (items) {
                            return list(refreshAll)
                        }
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

    return { data, items, get, list, create, update, remove }
}