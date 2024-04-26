export default defineNuxtRouteMiddleware((to, from) => {
    const user = userStore()
    const { getTokens, saveTokens, removeTokens } = useTokens()
    const publicRoutes = ['login', 'reset-password', 'mfa']
    user.check()
    if ((to.name === 'mfa' && !getTokens().mfa) || (!publicRoutes.includes(to.name) && !user.user)) {
        return navigateTo('/login')
    }
    else if (publicRoutes.includes(to.name) && user.user) {
        return navigateTo('/')
    }
})