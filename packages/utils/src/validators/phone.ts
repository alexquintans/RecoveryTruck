/**
 * Valida se um número de telefone está em formato válido
 * Aceita formatos: (99) 99999-9999 ou 99999999999
 */
export function isValidPhone(phone: string): boolean {
  // Remove caracteres não numéricos
  const cleanPhone = phone.replace(/\D/g, '');
  
  // Verifica se tem entre 10 e 11 dígitos (com ou sem DDD)
  if (cleanPhone.length < 10 || cleanPhone.length > 11) {
    return false;
  }
  
  // Se tiver 11 dígitos, o primeiro deve ser 9 (celular)
  if (cleanPhone.length === 11 && cleanPhone.charAt(0) !== '9') {
    return false;
  }
  
  return true;
}

/**
 * Formata um número de telefone para o formato brasileiro
 * (99) 99999-9999 ou (99) 9999-9999
 */
export function formatPhone(phone: string): string {
  // Remove caracteres não numéricos
  const cleanPhone = phone.replace(/\D/g, '');
  
  // Verifica se é celular (11 dígitos) ou fixo (10 dígitos)
  if (cleanPhone.length === 11) {
    // Celular: (99) 99999-9999
    return cleanPhone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  } else if (cleanPhone.length === 10) {
    // Fixo: (99) 9999-9999
    return cleanPhone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
  }
  
  // Se não estiver em um formato reconhecido, retorna como está
  return phone;
} 