/**
 * Formata um CPF para o formato brasileiro (123.456.789-00)
 */
export function formatCPF(cpf: string): string {
  // Remove caracteres não numéricos
  const cleanCPF = cpf.replace(/\D/g, '');
  
  // Verifica se tem 11 dígitos
  if (cleanCPF.length !== 11) {
    return cpf;
  }
  
  // Formata no padrão 123.456.789-00
  return cleanCPF.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

/**
 * Mascara um CPF para exibição parcial (***.***.789-00)
 */
export function maskCPF(cpf: string): string {
  // Remove caracteres não numéricos
  const cleanCPF = cpf.replace(/\D/g, '');
  
  // Verifica se tem 11 dígitos
  if (cleanCPF.length !== 11) {
    return cpf;
  }
  
  // Extrai os últimos 5 dígitos
  const lastDigits = cleanCPF.slice(-5);
  
  // Formata no padrão ***.***.789-00
  return `***.***.${ lastDigits.slice(0, 3) }-${ lastDigits.slice(3) }`;
} 