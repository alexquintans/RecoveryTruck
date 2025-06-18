/**
 * Utilitário para concatenar classes CSS
 */
export function cn(...inputs: (string | undefined | null | false)[]) {
  return inputs.filter(Boolean).join(' ');
} 