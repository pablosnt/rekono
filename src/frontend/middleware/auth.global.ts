export default defineNuxtRouteMiddleware((to, from) => {
    const user = userStore()
    const publicRoutes = ['login', 'reset-password', 'mfa']
    user.check()
    if (publicRoutes.includes(to.name) && user.user) {
        return navigateTo('/')
    } else if (!publicRoutes.includes(to.name) && !user.user) {
        return navigateTo('/login')
    }
})