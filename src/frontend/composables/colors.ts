export function useColors() {
    const stages = {}
    const intensities = {
        Sneaky: 'green',
        Low: 'blue',
        Normal: 'gray',
        Hard: 'orange',
        Insane: 'red'
    }
    
    return { stages, intensities }
}