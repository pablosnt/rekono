<script>
    import { userStore } from '@/stores/user'
    import { refreshStore } from '@/stores/refresh'
    import router from '@/router'
    import { toast } from 'vue3-toastify'
    export default {
        entity: null,
        endpoint: '/api/',
        authentication: true,
        headers: null,
        defaultHeaders: {
            'Content-Type': 'application/json',
            Accept: 'application/json'
        },
        getData: {},
        listData: [],
        refreshAfterCreation: true,
        refreshAfterDeletion: true,
        refreshAfterUpdate: true,
        refreshAll: false,
        page: 1,
        limit: 25,
        limits: [25, 50, 100],
        max_limit: 1000,
        total: 0,
        rootPath: import.meta.env.VITE_ROOT_PATH,
        backendUrl: import.meta.env.DESKTOP && import.meta.env.MODE == 'production'? import.meta.env.VITE_DESKTOP_BACKEND_URL : null,
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
        user: userStore(),
        refresh: refreshStore(),
        methods: {
            get(id) {
                this._request(`${this.endpoint}${id}/`, { method: 'GET', headers: this._headers(this.authentication) })
                    .then(response => { this.getData = response.json() })
            },
            list(all = false, page = 1) {
                limit = all ? this.max_limit : this.limit
                page = all ? page : this.page
                if (page === 1 && all) {
                    this.listData = []
                }
                this._request(this.endpoint, { method: 'GET', headers: this._headers(this.authentication), params: Object.assign({}, this._params(), { page: page, limit: limit })})
                    .then(response => {
                        const data = response.json()
                        this.total = data.count
                        this.listData = this.listData.concat(data.results)
                        if ((page * limit) < this.total && all) {
                            return this._request(page + 1, limit, all)
                        }
                    })
            },
            create(data) {
                if (!this._validate_creation(data)) { return }
                this._request(this.endpoint, { method: 'POST', headers: this._headers(this.authentication), body: data })
                    .then(() => {
                        if (this.refreshAfterCreation) {
                            this.list(this.refreshAll)
                        }
                        this._alert(`New ${entity.toLowerCase()} has been successfully created`, 'success')
                    })
            },
            update(id, data) {
                if (!this._validate_update(data)) { return }
                this._request(`${this.endpoint}${id}/`, { method: 'PUT', headers: this._headers(this.authentication), body: data })
                    .then(response => {
                        if (this.refreshAfterUpdate) {
                            if (this.getData) {
                                this.getData = response.json()
                            }
                            if (this.listData) {
                                this.list(this.refreshAll)
                            }
                        }
                    })
            },
            delete(id) {
                this._request(`${this.endpoint}${id}/`, { method: 'DELETE', headers: this._headers(this.authentication) })
                    .then(() => {
                        if (this.refreshAfterDeletion) {
                            this.list(this.refreshAll)
                        }
                        this._alert(`${entity} ${id} has been deleted`, 'warning')
                    })
            },
            _validate_creation(data) { return true },
            _validate_update(data) { return true },
            _refresh() {
                if (!this.refresh.refreshing) {
                    this.refresh.change()
                    return this._request('/api/security/refresh/', { method: 'POST', headers: this._headers(true), body: { refresh: sessionStorage.getItem(this.refreshToken) }})
                        .then(response => {
                            this._remove_tokens()
                            this._save_tokens(response.json())
                            this.refresh.change()
                            return Promise.resolve()
                        })
                        .catch(() => {
                            this._remove_tokens()
                            this.refresh.change()
                            router.push({ name: 'login' })
                            return Promise.reject()
                        })
                }
                return Promise.reject()
            },
            _request(endpoint, options = {}) {
                fetch(this._url(endpoint), options)
                    .then(response => { return Promise.resolve(response) })
                    .catch(error => {
                        if (error.response) {
                            const data = error.response.json()
                            var message = 'Unexpected error'
                            switch (error.response.status) {
                                case 401:
                                    return this._refresh()
                                        .then(() => { return this._request(endpoint, options) })
                                        .catch(() => { return this.refresh.refreshing ? this._request(endpoint, options) : Promise.reject() })
                                case 400:
                                    const value = Object.values(data)[0][0]
                                    message = `${Object.keys(data)[0]}: ${value.charAt(0).toUpperCase}${value.slice(1)}`
                                case 403:
                                    message = 'You are not authorized to perform this operation'
                                case 404:
                                    message = 'Resource not found'
                            }
                            this._alert(message, 'error')
                        }
                        return Promise.reject(error)
                    })
            },
            _url(endpoint) {
                endpoint = this.rootPath ? this.rootPath + endpoint : endpoint
                if (this.backendUrl) {
                    var url = new URL(this.backendUrl)
                    url.pathname = endpoint
                    return url.href
                }
                return endpoint
            },
            _headers(authentication) {
                headers =  this.defaultHeaders
                if (this.user !== null && authentication) {
                    headers.Authorization = `Bearer ${sessionStorage.getItem(this.accessToken)}`
                }
                return this.headers !== null ? Object.assign({}, headers, this.headers) : headers
            },
            _params() { return {} },
            _alert(message, type) {
                toast(message, {'theme': 'auto', 'type': type, 'position': 'bottom-right', 'transition': 'slyde'})
            },
            _save_tokens(data) {
                sessionStorage.setItem(this.accessToken, data.access)
                sessionStorage.setItem(this.refreshToken, data.refresh)
                this.user.login(data.access)
            },
            _remove_tokens() {
                sessionStorage.removeItem(this.accessToken)
                sessionStorage.removeItem(this.refreshToken)
            }
        }
    }
</script>