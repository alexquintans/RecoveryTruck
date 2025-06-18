import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Service, Customer, Payment, Ticket } from '../types';

interface TotemState {
  // Dados do fluxo
  currentStep: 'welcome' | 'service' | 'customer' | 'terms' | 'payment' | 'ticket';
  selectedService: Service | null;
  customerData: Customer | null;
  currentPayment: Payment | null;
  currentTicket: Ticket | null;
  
  // Estado da UI
  isLoading: boolean;
  error: string | null;
  
  // Ações
  setStep: (step: TotemState['currentStep']) => void;
  setService: (service: Service | null) => void;
  setCustomer: (customer: Customer | null) => void;
  setPayment: (payment: Payment | null) => void;
  setTicket: (ticket: Ticket | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

// Estado inicial
const initialState = {
  currentStep: 'welcome' as const,
  selectedService: null,
  customerData: null,
  currentPayment: null,
  currentTicket: null,
  isLoading: false,
  error: null,
};

// Criar a store
export const useTotemStore = create<TotemState>()(
  persist(
    (set) => ({
      ...initialState,
      
      // Ações
      setStep: (step) => set({ currentStep: step }),
      setService: (service) => set({ selectedService: service }),
      setCustomer: (customer) => set({ customerData: customer }),
      setPayment: (payment) => set({ currentPayment: payment }),
      setTicket: (ticket) => set({ currentTicket: ticket }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      reset: () => set(initialState),
    }),
    {
      name: 'totem-store',
      // Apenas persistir alguns campos
      partialize: (state) => ({
        selectedService: state.selectedService,
        customerData: state.customerData,
        currentStep: state.currentStep,
      }),
    }
  )
); 