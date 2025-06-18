/**
 * Formata um valor para o formato de moeda brasileira (R$ 1.234,56)
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
}

/**
 * Formata um valor para o formato de moeda brasileira sem o símbolo (1.234,56)
 */
export function formatCurrencyWithoutSymbol(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Converte uma string de moeda para número (R$ 1.234,56 -> 1234.56)
 */
export function parseCurrency(value: string): number {
  // Remove caracteres não numéricos, exceto vírgula e ponto
  const cleanValue = value.replace(/[^\d,.]/g, '');
  
  // Substitui vírgula por ponto para conversão correta
  const normalizedValue = cleanValue.replace(',', '.');
  
  return parseFloat(normalizedValue);
} 