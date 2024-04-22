export function usePagination() {
    const page = ref(1)
    const limit = ref(25)
    const total = ref(null)    
    const limits = [25, 50, 100]
    const max_limit = 1000

    return { page, limit, total, limits, max_limit }
}