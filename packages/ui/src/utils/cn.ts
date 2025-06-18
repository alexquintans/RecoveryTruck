import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Concatena classes CSS usando clsx e tailwind-merge
 * para evitar conflitos e duplicações
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
} 