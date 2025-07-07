export interface Customer {
  name: string;
  phone?: string;
  email?: string;
  document?: string;
  cpf?: string;
  termsAccepted?: boolean;
  termsAcceptedAt?: string;
  extras?: { id: string; quantity: number }[];
} 