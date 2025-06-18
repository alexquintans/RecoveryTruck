import { Service, Ticket, Payment, Customer, PaymentMethod } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Timeout para simular latência de rede
const MOCK_DELAY = 800;

/**
 * Cliente de API para o totem
 */
export const api = {
  /**
   * Busca todos os serviços disponíveis
   */
  async getServices(): Promise<Service[]> {
    try {
      const response = await fetch(`${API_URL}/services`);
      if (!response.ok) {
        throw new Error(`Erro ao buscar serviços: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Falha ao buscar serviços:', error);
      // Retorna dados mock em caso de falha
      await new Promise(resolve => setTimeout(resolve, MOCK_DELAY));
      return [
        {
          id: '1',
          name: 'Banheira de Gelo',
          description: 'Recuperação com banheira de gelo por 10 minutos',
          price: 50.0,
          duration: 10,
          slug: 'banheira-gelo',
          color: '#1A3A4A' // Cor primária
        },
        {
          id: '2',
          name: 'Bota de Compressão',
          description: 'Recuperação com bota de compressão por 10 minutos',
          price: 80.0,
          duration: 10,
          slug: 'bota-compressao',
          color: '#8AE65C' // Cor secundária
        }
      ];
    }
  },

  /**
   * Inicia um novo pagamento para o serviço selecionado
   */
  async createPayment(serviceId: string, customerData: Customer, paymentMethod: PaymentMethod): Promise<Payment> {
    try {
      const response = await fetch(`${API_URL}/payments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          serviceId,
          customerData,
          paymentMethod,
        }),
      });

      if (!response.ok) {
        throw new Error(`Erro ao criar pagamento: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Falha ao criar pagamento:', error);
      
      // Mock payment data
      await new Promise(resolve => setTimeout(resolve, MOCK_DELAY));
      
      // Buscar o serviço dos dados mock
      const services = await this.getServices();
      const service = services.find(s => s.id === serviceId);
      
      if (!service) {
        throw new Error('Serviço não encontrado');
      }
      
      const paymentId = `pay_${Math.random().toString(36).substring(2, 10)}`;
      
      // Dados específicos para cada método de pagamento
      let paymentData: Partial<Payment> = {};
      
      if (paymentMethod === 'pix') {
        paymentData = {
          qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=00020101021226870014br.gov.bcb.pix2565qrcodepix-h.bb.com.br/pix/v2/22657e78-7182-4473-ae3d-4c3ccac6cd454e',
          qrCodeText: '00020101021226870014br.gov.bcb.pix2565qrcodepix-h.bb.com.br/pix/v2/22657e78-7182-4473-ae3d-4c3ccac6cd454e'
        };
      } else if (paymentMethod === 'credit_card' || paymentMethod === 'debit_card') {
        // Dados específicos para pagamento com cartão
        paymentData = {
          transactionId: `trans_${Math.random().toString(36).substring(2, 10)}`
        };
      }
      
      return {
        id: paymentId,
        amount: service.price,
        method: paymentMethod,
        status: 'pending',
        serviceId: service.id,
        service: service,
        customerId: `cus_${Math.random().toString(36).substring(2, 10)}`,
        customer: customerData,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        ...paymentData
      };
    }
  },

  /**
   * Verifica o status de um pagamento
   */
  async checkPaymentStatus(paymentId: string): Promise<Payment> {
    try {
      const response = await fetch(`${API_URL}/payments/${paymentId}`);
      if (!response.ok) {
        throw new Error(`Erro ao verificar pagamento: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Falha ao verificar pagamento:', error);
      
      // Simula uma chance de 70% de pagamento concluído após alguns segundos
      await new Promise(resolve => setTimeout(resolve, MOCK_DELAY));
      
      const mockPayment = {
        id: paymentId,
        amount: 50.0,
        method: 'pix' as PaymentMethod,
        status: Math.random() > 0.3 ? 'completed' as const : 'pending' as const,
        serviceId: '1',
        createdAt: new Date(Date.now() - 60000).toISOString(),
        updatedAt: new Date().toISOString(),
        completedAt: Math.random() > 0.3 ? new Date().toISOString() : undefined,
        ticketId: Math.random() > 0.3 ? `tick_${Math.random().toString(36).substring(2, 10)}` : undefined
      };
      
      return mockPayment;
    }
  },

  /**
   * Busca um ticket pelo ID
   */
  async getTicket(ticketId: string): Promise<Ticket> {
    try {
      const response = await fetch(`${API_URL}/tickets/${ticketId}`);
      if (!response.ok) {
        throw new Error(`Erro ao buscar ticket: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Falha ao buscar ticket:', error);
      
      // Dados mock para ticket
      await new Promise(resolve => setTimeout(resolve, MOCK_DELAY));
      
      return {
        id: ticketId,
        number: 'A-007',
        serviceId: '1',
        status: 'in_queue',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        queuedAt: new Date().toISOString(),
        queuePosition: 3,
        estimatedWaitTime: 10
      };
    }
  },
  
  /**
   * Cria um novo ticket após o pagamento
   */
  async createTicket(paymentId: string): Promise<Ticket> {
    try {
      const response = await fetch(`${API_URL}/tickets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          paymentId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Erro ao criar ticket: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Falha ao criar ticket:', error);
      
      // Dados mock para ticket
      await new Promise(resolve => setTimeout(resolve, MOCK_DELAY));
      
      return {
        id: `tick_${Math.random().toString(36).substring(2, 10)}`,
        number: `A-${Math.floor(Math.random() * 100).toString().padStart(3, '0')}`,
        serviceId: '1',
        status: 'in_queue',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        queuedAt: new Date().toISOString(),
        queuePosition: Math.floor(Math.random() * 5) + 1,
        estimatedWaitTime: 10
      };
    }
  }
}; 