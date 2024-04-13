<script>
    import { userStore } from '@/stores/user'
    import { refreshStore } from '@/stores/refresh'
    import router from '@/router'
    import { toast } from 'vue3-toastify'
    export default {
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
        updateGetData: true,
        rootPath: import.meta.env.VITE_ROOT_PATH,
        backendUrl: import.meta.env.DESKTOP && import.meta.env.MODE == 'production'? import.meta.env.VITE_DESKTOP_BACKEND_URL : null,
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
        user: userStore(),
        refresh: refreshStore(),
        methods: {
            get(id) {},
            list(page = 1, pagination = false) {},
            create() {},
            update() {},
            delete() {},
            _refresh() {
                if (!this.refresh.refreshing) {
                    this.refresh.change()
                    return this._request('/api/security/refresh/', { method: 'POST', headers: this._headers(true), body: { refresh: sessionStorage.getItem(this.refreshToken) }})
                        .then(response => {
                            this._remove_tokens()
                            this._save_tokens(response.data)
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
                            var message = 'Unexpected error'
                            switch (error.response.status) {
                                case 401:
                                    return this._refresh()
                                        .then(() => { return this._request(endpoint, options) })
                                        .catch(() => { return this.refresh.refreshing ? this._request(endpoint, options) : Promise.reject() })
                                case 400:
                                    const value = Object.values(error.response.data)[0][0]
                                    message = `${Object.keys(error.response.data)[0]}: ${value.charAt(0).toUpperCase}${value.slice(1)}`
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