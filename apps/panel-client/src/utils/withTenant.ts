import { getAuthUser } from '@totem/utils';
 
export function withTenant(params: Record<string, any> = {}) {
  const user = getAuthUser();
  const result = { ...params };
  if (user?.tenant_id) {
    result.tenant_id = user.tenant_id;
  }
  return result;
} 