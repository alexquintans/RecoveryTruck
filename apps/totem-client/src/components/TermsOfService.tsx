import React from 'react';
import type { Service } from '../types';

interface TermsOfServiceProps {
  service?: Service;
}

export const TermsOfService: React.FC<TermsOfServiceProps> = ({ service }) => {
  return (
    <div className="terms-of-service text-text">
      <h3 className="text-xl font-bold mb-4">Termo de Responsabilidade - RecoveryTruck</h3>
      
      <p className="mb-4">
        Data: {new Date().toLocaleDateString('pt-BR')}
      </p>
      
      <h4 className="text-lg font-semibold mb-2">1. Declaração de Saúde</h4>
      <p className="mb-4">
        Declaro estar em condições físicas adequadas para realizar o procedimento de {service?.name || "recuperação física"} e que não possuo nenhuma das contraindicações listadas abaixo:
      </p>
      <ul className="list-disc pl-6 mb-4">
        <li className="mb-1">Ferimentos abertos ou lesões cutâneas na área a ser tratada</li>
        <li className="mb-1">Trombose venosa profunda ou histórico recente de coágulos sanguíneos</li>
        <li className="mb-1">Doenças cardíacas graves ou hipertensão não controlada</li>
        <li className="mb-1">Gravidez (em caso de dúvida, consulte seu médico)</li>
        <li className="mb-1">Sensibilidade extrema ao frio ou calor</li>
        <li className="mb-1">Neuropatia periférica grave</li>
      </ul>
      
      <h4 className="text-lg font-semibold mb-2">2. Riscos e Efeitos Colaterais</h4>
      <p className="mb-4">
        Estou ciente de que o procedimento de {service?.name || "recuperação física"} pode apresentar os seguintes efeitos colaterais:
      </p>
      <ul className="list-disc pl-6 mb-4">
        <li className="mb-1">Desconforto temporário durante o procedimento</li>
        <li className="mb-1">Vermelhidão ou irritação temporária na pele</li>
        <li className="mb-1">Sensação de dormência temporária</li>
        {service?.slug === 'banheira-gelo' && (
          <li className="mb-1">Sensibilidade ao frio por algumas horas após o procedimento</li>
        )}
        {service?.slug === 'bota-compressao' && (
          <li className="mb-1">Sensação de pressão durante o procedimento</li>
        )}
      </ul>
      
      <h4 className="text-lg font-semibold mb-2">3. Consentimento</h4>
      <p className="mb-4">
        Ao assinar este termo, declaro que:
      </p>
      <ul className="list-disc pl-6 mb-4">
        <li className="mb-1">Li e compreendi todas as informações acima</li>
        <li className="mb-1">Tive a oportunidade de esclarecer todas as minhas dúvidas</li>
        <li className="mb-1">Autorizo a realização do procedimento de {service?.name || "recuperação física"}</li>
        <li className="mb-1">Concordo em seguir todas as orientações pré e pós-procedimento</li>
        <li className="mb-1">Isento a RecoveryTruck de responsabilidade por complicações decorrentes do não cumprimento das recomendações</li>
      </ul>
      
      <h4 className="text-lg font-semibold mb-2">4. Duração e Expectativas</h4>
      <p className="mb-4">
        O procedimento de {service?.name || "recuperação física"} tem duração de {service?.duration || 10} minutos. Os resultados podem variar de acordo com cada organismo e condição física individual.
      </p>
      
      <h4 className="text-lg font-semibold mb-2">5. Orientações Importantes</h4>
      <p className="mb-2">Para obter os melhores resultados:</p>
      <ul className="list-disc pl-6 mb-4">
        <li className="mb-1">Mantenha-se hidratado antes e depois do procedimento</li>
        <li className="mb-1">Informe imediatamente ao profissional caso sinta qualquer desconforto excessivo</li>
        <li className="mb-1">Siga todas as instruções fornecidas pelo profissional durante o procedimento</li>
        <li className="mb-1">Evite atividades físicas intensas por pelo menos 2 horas após o procedimento</li>
      </ul>
      
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="font-semibold">
          Ao prosseguir, confirmo que li, compreendi e concordo com todos os termos acima.
        </p>
      </div>
    </div>
  );
}; 