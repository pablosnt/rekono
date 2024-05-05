export function useEnums() {
    const stages = {
        OSINT: {
            id: 1,
            color: 'green'
        },
        Enumeration: {
            id: 2,
            color: 'purple'
        },
        Vulnerabilities: {
            id: 3,
            color: 'orange'
        },
        Services: {
            id: 4,
            color: 'blue'
        },
        Exploitation: {
            id: 5,
            color: 'red'
        },
    }
    const intensities = {
        Sneaky: {
            id: 1,
            color: 'green',
        },
        Low: {
            id: 2,
            color: 'blue',
        },
        Normal: {
            id: 3,
            color: 'gray',
        },
        Hard: {
            id: 4,
            color: 'orange',
        },
        Insane: {
            id: 5,
            color: 'red',
        }
    }
    const wordlists = ['Subdomain', 'Endpoint']
    
    return { stages, intensities, wordlists }
}