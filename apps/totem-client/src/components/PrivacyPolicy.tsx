import React from 'react';

export const PrivacyPolicy: React.FC = () => {
  return (
    <div className="privacy-policy text-text">
      <h3 className="text-xl font-bold mb-4">Política de Privacidade - RecoveryTruck</h3>
      
      <p className="mb-4">
        Última atualização: {new Date().toLocaleDateString('pt-BR')}
      </p>
      
      <h4 className="text-lg font-semibold mb-2">1. Introdução</h4>
      <p className="mb-4">
        A RecoveryTruck está comprometida em proteger sua privacidade. Esta Política de Privacidade explica como coletamos, usamos, divulgamos e protegemos suas informações pessoais quando você utiliza nossos serviços de recuperação física.
      </p>
      
      <h4 className="text-lg font-semibold mb-2">2. Informações que Coletamos</h4>
      <p className="mb-2">Podemos coletar os seguintes tipos de informações:</p>
      <ul className="list-disc pl-6 mb-4">
        <li className="mb-1">Informações pessoais: nome completo, CPF e telefone</li>
        <li className="mb-1">Informações de uso: serviços utilizados, frequência e preferências</li>
        <li className="mb-1">Informações de pagamento: registros de transações (não armazenamos dados de cartão)</li>
      </ul>
      
      <h4 className="text-lg font-semibold mb-2">3. Como Usamos suas Informações</h4>
      <p className="mb-2">Utilizamos suas informações para:</p>
      <ul className="list-disc pl-6 mb-4">
        <li className="mb-1">Fornecer, manter e melhorar nossos serviços</li>
        <li className="mb-1">Processar pagamentos e gerar tickets de atendimento</li>
        <li className="mb-1">Enviar notificações relacionadas ao serviço</li>
        <li className="mb-1">Personalizar sua experiência</li>
        <li className="mb-1">Cumprir obrigações legais</li>
      </ul>
      
      <h4 className="text-lg font-semibold mb-2">4. Compartilhamento de Informações</h4>
      <p className="mb-4">
        Não vendemos suas informações pessoais. Podemos compartilhar informações com:
      </p>
      <ul className="list-disc pl-6 mb-4">
        <li className="mb-1">Prestadores de serviços que nos ajudam a operar nossos serviços</li>
        <li className="mb-1">Autoridades governamentais quando exigido por lei</li>
      </ul>
      
      <h4 className="text-lg font-semibold mb-2">5. Segurança de Dados</h4>
      <p className="mb-4">
        Implementamos medidas de segurança para proteger suas informações contra acesso não autorizado, alteração, divulgação ou destruição.
      </p>
      
      <h4 className="text-lg font-semibold mb-2">6. Seus Direitos</h4>
      <p className="mb-2">Você tem direito a:</p>
      <ul className="list-disc pl-6 mb-4">
        <li className="mb-1">Acessar seus dados pessoais</li>
        <li className="mb-1">Corrigir dados imprecisos</li>
        <li className="mb-1">Solicitar a exclusão de seus dados</li>
        <li className="mb-1">Restringir ou opor-se ao processamento de seus dados</li>
        <li className="mb-1">Solicitar a portabilidade de seus dados</li>
      </ul>
      
      <h4 className="text-lg font-semibold mb-2">7. Alterações nesta Política</h4>
      <p className="mb-4">
        Podemos atualizar esta Política de Privacidade periodicamente. Notificaremos sobre alterações significativas através de um aviso em nosso serviço ou por outros meios.
      </p>
      
      <h4 className="text-lg font-semibold mb-2">8. Contato</h4>
      <p className="mb-4">
        Se você tiver dúvidas sobre esta Política de Privacidade, entre em contato conosco pelo e-mail: privacidade@recoverytruck.com.br
      </p>
    </div>
  );
}; 