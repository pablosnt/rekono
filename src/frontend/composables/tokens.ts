export function useTokens() {
    const mfaToken = 'mfa-token'
    const accessToken = 'access-token'
    const refreshToken = 'refresh-token'
    const user = userStore()

    function getTokens(): object {
        return {
            access: sessionStorage.getItem(accessToken),
            refresh: sessionStorage.getItem(refreshToken),
            mfa: sessionStorage.getItem(mfaToken)
        }
    }

    function saveTokens(data: object): boolean {
        if (data.access) {
            removeTokens()
            sessionStorage.setItem(accessToken, data.access)
            sessionStorage.setItem(refreshToken, data.refresh)
            user.login(data.access)
            return true
        } else if (data.mfa) {
            removeTokens()
            sessionStorage.setItem(mfaToken, data.mfa)
            return false
        }
        throw new Error('User not authenticated')
    }

    function removeTokens() {
        sessionStorage.removeItem(accessToken)
        sessionStorage.removeItem(refreshToken)
        sessionStorage.removeItem(mfaToken)
    }

    return { getTokens, saveTokens, removeTokens }
}