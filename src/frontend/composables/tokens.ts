export function useTokens() {
    const mfaToken = 'mfa-token'
    const accessToken = 'access-token'
    const refreshToken = 'refresh-token'
    const user = userStore()

    function get(): object {
        return {
            access: sessionStorage.getItem(accessToken),
            refresh: sessionStorage.getItem(refreshToken),
            mfa: sessionStorage.getItem(mfaToken)
        }
    }

    function save(data: object): boolean {
        if (data.access) {
            remove()
            sessionStorage.setItem(accessToken, data.access)
            sessionStorage.setItem(refreshToken, data.refresh)
            user.login(data.access)
            return true
        } else if (data.mfa) {
            remove()
            sessionStorage.setItem(mfaToken, data.mfa)
            return false
        }
        throw new Error('User not authenticated')
    }

    function remove() {
        sessionStorage.removeItem(accessToken)
        sessionStorage.removeItem(refreshToken)
        sessionStorage.removeItem(mfaToken)
    }

    return { get, save, remove }
}