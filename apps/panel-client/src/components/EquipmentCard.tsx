import React from 'react';
import { FaSnowflake, FaSpa, FaBath, FaSocks, FaTools, FaExclamationTriangle } from 'react-icons/fa';
import type { Equipment, EquipmentType } from '../types';

interface EquipmentCardProps {
  equipamento: Equipment;
  selecionado?: boolean;
  onClick?: () => void;
  className?: string;
  realStatus?: {
    status: string;
    in_use: boolean;
    assigned_operator_id?: string;
  };
}

const nameCorrections: Record<string, string> = {
  'ofur': 'Ofurô',
  'crioterapia': 'Crioterapia',
  'bota_de_compress_o': 'Bota de Compressão',
  'massoterapia': 'Massoterapia',
};

function formatEquipmentName(identifier: string) {
  return identifier
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => nameCorrections[word.toLowerCase()] || (word.charAt(0).toUpperCase() + word.slice(1)))
    .join(' ');
}

function formatEquipmentType(type: string) {
  switch (type) {
    case 'banheira_gelo': return 'Banheira de Gelo';
    case 'bota_compressao': return 'Bota de Compressão';
    case 'ofuro': return 'Ofurô';
    case 'massoterapia': return 'Massoterapia';
    case 'crioterapia': return 'Crioterapia';
    case 'totem': return 'Totem';
    default: return type.charAt(0).toUpperCase() + type.slice(1);
  }
}

function getEquipmentIcon(type: string): React.ReactElement {
  switch (type) {
    case 'banheira_gelo':
    case 'crioterapia':
      return <FaSnowflake className="text-[#3B82F6] text-5xl" />;
    case 'bota_compressao':
      return <FaSocks className="text-[#1F526B] text-5xl" />;
    case 'ofuro':
      return <FaBath className="text-[#3B82F6] text-5xl" />;
    case 'massoterapia':
      return <FaSpa className="text-[#3B82F6] text-5xl" />;
    default:
      return <FaTools className="text-[#666666] text-5xl" />;
  }
}

function getStatusInfo(realStatus?: EquipmentCardProps['realStatus']) {
  if (!realStatus) {
    return {
      badge: <span className="bg-[#F0F8FF] text-[#3B82F6] px-3 py-0.5 rounded-full text-xs font-medium mt-2">Disponível</span>,
      color: 'text-[#3B82F6]',
      bgColor: 'bg-[#F0F8FF]',
      borderColor: 'border-[#3B82F6]',
      isDisabled: false
    };
  }

  if (realStatus.in_use) {
    return {
      badge: <span className="bg-[#FFF8E1] text-[#F59E0B] px-3 py-0.5 rounded-full text-xs font-medium mt-2 flex items-center gap-1">
        <FaExclamationTriangle className="text-xs" />
        Em uso
      </span>,
      color: 'text-[#F59E0B]',
      bgColor: 'bg-[#FFF8E1]',
      borderColor: 'border-[#F59E0B]',
      isDisabled: true
    };
  }

  if (realStatus.status === 'maintenance') {
    return {
      badge: <span className="bg-[#FEF2F2] text-[#EF4444] px-3 py-0.5 rounded-full text-xs font-medium mt-2">Manutenção</span>,
      color: 'text-[#EF4444]',
      bgColor: 'bg-[#FEF2F2]',
      borderColor: 'border-[#EF4444]',
      isDisabled: true
    };
  }

  if (realStatus.status === 'offline') {
    return {
      badge: <span className="bg-[#F3F4F6] text-[#6B7280] px-3 py-0.5 rounded-full text-xs font-medium mt-2">Offline</span>,
      color: 'text-[#6B7280]',
      bgColor: 'bg-[#F3F4F6]',
      borderColor: 'border-[#6B7280]',
      isDisabled: true
    };
  }

  return {
    badge: <span className="bg-[#F0F8FF] text-[#3B82F6] px-3 py-0.5 rounded-full text-xs font-medium mt-2">Disponível</span>,
    color: 'text-[#3B82F6]',
    bgColor: 'bg-[#F0F8FF]',
    borderColor: 'border-[#3B82F6]',
    isDisabled: false
  };
}

export const EquipmentCard: React.FC<EquipmentCardProps> = (props: EquipmentCardProps) => {
  const { equipamento, selecionado = false, onClick, className = '', realStatus } = props;
  
  const statusInfo = getStatusInfo(realStatus);
  const isDisabled = statusInfo.isDisabled || realStatus?.in_use;

  return (
    <button
      className={`
        flex flex-col items-center justify-center gap-1 px-6 py-6 min-h-[180px] rounded-2xl border-2 shadow-lg transition-all duration-200
        ${selecionado && !isDisabled ? 'border-[#3B82F6] bg-[#F0F8FF] scale-105 shadow-xl' : 
          isDisabled ? 'border-[#D9D9D9] bg-gray-50 opacity-60 cursor-not-allowed' :
          'border-[#D9D9D9] bg-white hover:border-[#3B82F6] hover:-translate-y-1 hover:shadow-xl'}
        focus:outline-none focus:ring-2 focus:ring-[#3B82F6]
        text-center
        ${className}
      `}
      title={`${formatEquipmentName(equipamento.name)} - Status: ${realStatus?.status || 'available'} ${realStatus?.in_use ? '(Em uso)' : ''}`}
      onClick={isDisabled ? undefined : onClick}
      tabIndex={isDisabled ? -1 : 0}
      aria-pressed={!!selecionado}
      aria-label={`Equipamento ${formatEquipmentName(equipamento.name)}, status: ${realStatus?.status || 'available'}`}
      aria-disabled={isDisabled}
      type="button"
    >
      <div className={`${isDisabled ? 'opacity-50' : ''}`}>
        {getEquipmentIcon(equipamento.type)}
      </div>
      <span className={`font-bold text-lg mt-2 mb-0.5 ${isDisabled ? 'text-gray-500' : 'text-gray-800'}`}>
        {formatEquipmentName(equipamento.name)}
      </span>
      <span className="text-xs text-gray-500 mb-1">{formatEquipmentType(equipamento.type)}</span>
      {statusInfo.badge}
      
      {/* ✅ NOVO: Mostrar operador responsável se estiver em uso */}
      {realStatus?.in_use && realStatus.assigned_operator_id && (
        <span className="text-xs text-gray-400 mt-1">
          Operador: {realStatus.assigned_operator_id.slice(0, 8)}...
        </span>
      )}
    </button>
  );
}; 