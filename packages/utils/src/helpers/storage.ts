interface StorageItem<T> {
  value: T;
  expiry?: number;
}

/**
 * Salva um item no localStorage com suporte a expiração
 * @param key Chave para armazenamento
 * @param value Valor a ser armazenado
 * @param ttlMinutes Tempo de vida em minutos (opcional)
 */
export function setStorageItem<T>(key: string, value: T, ttlMinutes?: number): void {
  const item: StorageItem<T> = {
    value,
  };
  
  // Adiciona expiração se ttlMinutes for fornecido
  if (ttlMinutes) {
    const now = new Date();
    item.expiry = now.getTime() + ttlMinutes * 60 * 1000;
  }
  
  localStorage.setItem(key, JSON.stringify(item));
}

/**
 * Obtém um item do localStorage, verificando sua expiração
 * @param key Chave do item
 * @returns O valor armazenado ou null se não existir ou estiver expirado
 */
export function getStorageItem<T>(key: string): T | null {
  const itemStr = localStorage.getItem(key);
  
  // Retorna null se o item não existir
  if (!itemStr) {
    return null;
  }
  
  try {
    const item: StorageItem<T> = JSON.parse(itemStr);
    
    // Verifica se o item expirou
    if (item.expiry && new Date().getTime() > item.expiry) {
      // Remove o item expirado
      localStorage.removeItem(key);
      return null;
    }
    
    return item.value;
  } catch (error) {
    // Em caso de erro no parsing, remove o item
    localStorage.removeItem(key);
    return null;
  }
}

/**
 * Remove um item do localStorage
 * @param key Chave do item a ser removido
 */
export function removeStorageItem(key: string): void {
  localStorage.removeItem(key);
}

/**
 * Limpa todos os itens armazenados pelo aplicativo
 * @param prefix Prefixo opcional para limpar apenas itens específicos
 */
export function clearStorage(prefix?: string): void {
  if (prefix) {
    // Remove apenas itens com o prefixo especificado
    Object.keys(localStorage)
      .filter(key => key.startsWith(prefix))
      .forEach(key => localStorage.removeItem(key));
  } else {
    // Remove todos os itens
    localStorage.clear();
  }
} 