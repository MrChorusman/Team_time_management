import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combina clases de CSS usando clsx y tailwind-merge
 * @param {...any} inputs - Clases de CSS a combinar
 * @returns {string} - Clases combinadas
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

