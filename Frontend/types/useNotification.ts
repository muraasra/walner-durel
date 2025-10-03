export const useNotification = () => {
  const toasts = useState('toasts', () => [] as {
    id: string
    message: string
    type: 'success' | 'error' | 'info'
    duration: number
  }[]);

  const addToast = (message: string, type: 'success' | 'error' | 'info' = 'info', duration = 3000) => {
    const id = `toast-${Date.now()}`;
    const toast = { id, message, type, duration };
    toasts.value.push(toast);

    if (duration > 0) {
      setTimeout(() => {
        toasts.value = toasts.value.filter(t => t.id !== id);
      }, duration);
    }
  };

  return {
    toasts,
    addToast,
    success: (message: string, duration?: number) => addToast(message, 'success', duration),
    errors: (message: string, duration?: number) => addToast(message, 'error', duration),
    info: (message: string, duration?: number) => addToast(message, 'info', duration),
  };
};
