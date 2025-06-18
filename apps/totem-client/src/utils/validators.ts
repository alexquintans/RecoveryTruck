/**
 * Validador de CPF
 * @param cpf CPF a ser validado (pode conter pontuação)
 * @returns true se o CPF for válido, false caso contrário
 */
export const validateCPF = (cpf: string): boolean => {
  // Remove caracteres não numéricos
  cpf = cpf.replace(/[^\d]/g, '');
  
  // Verifica se tem 11 dígitos
  if (cpf.length !== 11) return false;
  
  // Verifica se todos os dígitos são iguais
  if (/^(\d)\1+$/.test(cpf)) return false;
  
  // Validação do primeiro dígito verificador
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cpf.charAt(i)) * (10 - i);
  }
  let remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.charAt(9))) return false;
  
  // Validação do segundo dígito verificador
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cpf.charAt(i)) * (11 - i);
  }
  remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.charAt(10))) return false;
  
  return true;
};

/**
 * Validador de telefone brasileiro
 * @param phone Telefone a ser validado (formato: (00) 00000-0000)
 * @returns true se o telefone for válido, false caso contrário
 */
export const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^\(\d{2}\) \d{5}-\d{4}$/;
  return phoneRegex.test(phone);
};

/**
 * Validador de e-mail
 * @param email E-mail a ser validado
 * @returns true se o e-mail for válido, false caso contrário
 */
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validador de nome
 * @param name Nome a ser validado
 * @param minLength Tamanho mínimo (padrão: 3)
 * @returns true se o nome for válido, false caso contrário
 */
export const validateName = (name: string, minLength = 3): boolean => {
  return name.trim().length >= minLength;
}; 