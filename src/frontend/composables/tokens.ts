export function useTokens() {
    const mfaToken = 'mfa-token'
    const accessToken = 'access-token'
    const refreshToken = 'refresh-token'
    const user = userStore()

    function get(): object {
        return {
            access: localStorage.getItem(accessToken),
            refresh: localStorage.getItem(refreshToken),
            mfa: sessionStorage.getItem(mfaToken)
        }
    }

    function save(data: object): boolean {
        if (data) {
            if (data.access) {
                remove()
                localStorage.setItem(accessToken, data.access)
                localStorage.setItem(refreshToken, data.refresh)
                user.login(data.access)
                return true
            } else if (data.mfa) {
                remove()
                sessionStorage.setItem(mfaToken, data.mfa)
                return false
            }
        }
        throw new Error('User not authenticated')
    }

    function remove() {
        localStorage.removeItem(accessToken)
        localStorage.removeItem(refreshToken)
        sessionStorage.removeItem(mfaToken)
    }

    return { get, save, remove }
}