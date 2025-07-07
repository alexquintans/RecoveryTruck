// @jsxImportSource react
import * as React from 'react';
import { FaSnowflake, FaSpa, FaBath, FaSocks, FaTools } from 'react-icons/fa';
import type { Equipment } from '../types';

interface EquipmentCardProps {
  equipamento: Equipment;
  selecionado?: boolean;
  onClick?: () => void;
  className?: string;
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

function getEquipmentIcon(type: Equipment['type']): React.ReactElement {
  switch (type) {
    case 'banheira_gelo':
    case 'crioterapia':
      return <FaSnowflake className="text-blue-400 text-5xl" />;
    case 'bota_compressao':
      return <FaSocks className="text-yellow-400 text-5xl" />;
    case 'ofuro':
      return <FaBath className="text-indigo-400 text-5xl" />;
    case 'massoterapia':
      return <FaSpa className="text-green-400 text-5xl" />;
    default:
      return <FaTools className="text-gray-400 text-5xl" />;
  }
}

function statusBadge(status: Equipment['status']): React.ReactElement | null {
  if (status === 'available')
    return <span className="bg-green-50 text-green-600 px-3 py-0.5 rounded-full text-xs font-medium mt-2">Disponível</span>;
  if (status === 'in_use')
    return <span className="bg-yellow-50 text-yellow-700 px-3 py-0.5 rounded-full text-xs font-medium mt-2">Em uso</span>;
  if (status === 'maintenance')
    return <span className="bg-red-50 text-red-600 px-3 py-0.5 rounded-full text-xs font-medium mt-2">Manutenção</span>;
  return null;
}

export const EquipmentCard: React.FC<EquipmentCardProps> = (props: EquipmentCardProps) => {
  const { equipamento, selecionado = false, onClick, className = '' } = props;
  return (
    <button
      className={`
        flex flex-col items-center justify-center gap-1 px-6 py-6 min-h-[180px] rounded-2xl border-2 shadow-lg transition-all duration-200
        ${selecionado ? 'border-blue-600 bg-blue-50 scale-105 shadow-xl' : 'border-gray-200 bg-white hover:border-blue-400 hover:-translate-y-1 hover:shadow-xl'}
        focus:outline-none focus:ring-2 focus:ring-blue-400
        text-center
        ${className}
      `}
      title={formatEquipmentName(equipamento.name)}
      onClick={onClick}
      tabIndex={0}
      aria-pressed={!!selecionado}
      aria-label={`Equipamento ${formatEquipmentName(equipamento.name)}, status: ${equipamento.status}`}
      type="button"
    >
      {getEquipmentIcon(equipamento.type)}
      <span className="font-bold text-lg mt-2 mb-0.5 text-gray-800">{formatEquipmentName(equipamento.name)}</span>
      <span className="text-xs text-gray-500 mb-1">{formatEquipmentType(equipamento.type)}</span>
      {statusBadge(equipamento.status)}
    </button>
  );
}; 