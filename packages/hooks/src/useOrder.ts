import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Service {
  id: string;
  name: string;
  price: number;
  description: string;
  duration: number;
  slug: string;
}

export interface Customer {
  name: string;
  cpf?: string;
  phone?: string;
  email?: string;
  consentTerms: boolean;
}

export interface OrderState {
  service: Service | null;
  customer: Customer | null;
  paymentId: string | null;
  ticketNumber: string | null;
  step: 'service' | 'customer' | 'payment' | 'confirmation' | 'ticket';
  isLoading: boolean;
  error: string | null;
  
  // Ações
  setService: (service: Service | null) => void;
  setCustomer: (customer: Customer | null) => void;
  setPaymentId: (id: string | null) => void;
  setTicketNumber: (number: string | null) => void;
  setStep: (step: OrderState['step']) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

// Estado inicial
const initialState = {
  service: null,
  customer: null,
  paymentId: null,
  ticketNumber: null,
  step: 'service' as const,
  isLoading: false,
  error: null,
};

// Criar store com persistência
export const useOrderStore = create<OrderState>()(
  persist(
    (set) => ({
      ...initialState,
      
      // Ações
      setService: (service) => set({ service }),
      setCustomer: (customer) => set({ customer }),
      setPaymentId: (paymentId) => set({ paymentId }),
      setTicketNumber: (ticketNumber) => set({ ticketNumber }),
      setStep: (step) => set({ step }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      reset: () => set(initialState),
    }),
    {
      name: 'totem-order-storage',
      // Apenas persistir alguns campos
      partialize: (state) => ({
        service: state.service,
        customer: state.customer,
        step: state.step,
      }),
    }
  )
);

// Hook para usar a store
export function useOrder() {
  return useOrderStore();
} 