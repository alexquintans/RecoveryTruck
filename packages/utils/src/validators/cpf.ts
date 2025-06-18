/**
 * Valida se um CPF é válido
 */
export function isValidCPF(cpf: string): boolean {
  // Remove caracteres não numéricos
  const cleanCPF = cpf.replace(/\D/g, '');
  
  // Verifica se tem 11 dígitos
  if (cleanCPF.length !== 11) {
    return false;
  }
  
  // Verifica se todos os dígitos são iguais
  if (/^(\d)\1+$/.test(cleanCPF)) {
    return false;
  }
  
  // Validação do primeiro dígito verificador
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleanCPF.charAt(i)) * (10 - i);
  }
  let remainder = sum % 11;
  const digit1 = remainder < 2 ? 0 : 11 - remainder;
  
  // Validação do segundo dígito verificador
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleanCPF.charAt(i)) * (11 - i);
  }
  remainder = sum % 11;
  const digit2 = remainder < 2 ? 0 : 11 - remainder;
  
  // Verifica se os dígitos calculados são iguais aos dígitos do CPF
  return (
    parseInt(cleanCPF.charAt(9)) === digit1 &&
    parseInt(cleanCPF.charAt(10)) === digit2
  );
} 