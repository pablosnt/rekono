import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';


export function useAlert() {
    function alert(message: string, type: string) {
        toast(message, {
            'theme': 'colored',
            'type': type,
            'position': 'bottom-right',
            'transition': 'slyde'
        })
    }

    return alert
}