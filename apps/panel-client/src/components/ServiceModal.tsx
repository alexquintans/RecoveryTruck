import React, { useState } from 'react';
import { Modal } from './Modal';
import { PlusIcon } from '@heroicons/react/24/solid';

interface ServiceForm {
  name: string;
  description: string;
  price: number;
  duration: number;
  equipment_count: number;
  type: string;
  color: string;
  isActive: boolean;
}

interface ServiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: Partial<ServiceForm>;
  onSubmit: (data: any) => void;
}

const defaultForm: ServiceForm = {
  name: '',
  description: '',
  price: 0,
  duration: 10,
  equipment_count: 1,
  type: '',
  color: 'blue',
  isActive: true,
};

export const ServiceModal: React.FC<ServiceModalProps> = ({ isOpen, onClose, initialData, onSubmit }) => {
  const [form, setForm] = useState<ServiceForm>({ ...defaultForm, ...initialData });
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const required = ['name', 'description', 'price', 'duration', 'type', 'equipment_count'];
  const isValid = required.every(f => {
    const value = form[f as keyof ServiceForm];
    if (f === 'price' || f === 'duration' || f === 'equipment_count') {
      return value > 0;
    }
    return String(value).trim() !== '';
  });

  const handleBlur = (field: string) => setTouched(prev => ({ ...prev, [field]: true }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) {
      // console.log('Formulário inválido:', form);
      return;
    }
    
    // Mapeamento dos campos para o backend
    const payload = {
      name: form.name.trim(),
      description: form.description.trim(),
      price: Number(form.price),
      duration_minutes: Number(form.duration),
      equipment_count: Number(form.equipment_count),
      type: form.type.trim(),
      color: form.color,
      is_active: form.isActive,
    };
    
    // console.log('Payload sendo enviado:', payload);
    
    onSubmit(payload);
    onClose();
    setForm(defaultForm);
    setTouched({});
  };

  const closeAndReset = () => {
    onClose();
    setForm(defaultForm);
    setTouched({});
  };

  return (
    <Modal isOpen={isOpen} onClose={closeAndReset}>
      <button
        className="absolute top-4 right-4 text-gray-400 hover:text-[#18446B] text-2xl"
        onClick={closeAndReset}
        aria-label="Fechar"
        type="button"
      >×</button>
      <h2 className="text-2xl font-bold text-[#1F526B] mb-6 flex items-center gap-2">
        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#3B82F6] text-white">
          <svg width="22" height="22" fill="none" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" stroke="white" strokeWidth="2" strokeLinecap="round"/></svg>
        </span>
        {initialData ? 'Editar Serviço' : 'Adicionar Serviço'}
      </h2>
      <form onSubmit={handleSubmit} autoComplete="off">
        <div className="space-y-4">
          <input
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            onBlur={() => handleBlur('name')}
            placeholder="Nome do serviço *"
            className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#3B82F6] focus:ring-2 focus:ring-[#3B82F6] bg-white text-[#1F526B] text-base ${touched.name && !form.name ? 'border-red-500' : 'border-gray-300'}`}
            autoFocus
          />
          <textarea
            value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })}
            onBlur={() => handleBlur('description')}
            placeholder="Descrição do serviço *"
            className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#3B82F6] focus:ring-2 focus:ring-[#3B82F6] bg-white text-[#1F526B] text-base ${touched.description && !form.description ? 'border-red-500' : 'border-gray-300'}`}
            rows={2}
          />
          <div className="flex gap-4">
            <input
              type="number"
              value={form.price}
              onChange={e => setForm({ ...form, price: Number(e.target.value) })}
              onBlur={() => handleBlur('price')}
              placeholder="Preço (R$) *"
              className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#3B82F6] focus:ring-2 focus:ring-[#3B82F6] bg-white text-[#1F526B] text-base ${touched.price && !form.price ? 'border-red-500' : 'border-gray-300'}`}
            />
            <input
              type="number"
              value={form.duration}
              onChange={e => setForm({ ...form, duration: Number(e.target.value) })}
              onBlur={() => handleBlur('duration')}
              placeholder="Duração (min) *"
              className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#3B82F6] focus:ring-2 focus:ring-[#3B82F6] bg-white text-[#1F526B] text-base ${touched.duration && !form.duration ? 'border-red-500' : 'border-gray-300'}`}
            />
            <input
              type="number"
              value={form.equipment_count}
              onChange={e => setForm({ ...form, equipment_count: Number(e.target.value) })}
              onBlur={() => handleBlur('equipment_count')}
              placeholder="Qtde Equipamentos *"
              className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#3B82F6] focus:ring-2 focus:ring-[#3B82F6] bg-white text-[#1F526B] text-base ${touched.equipment_count && !form.equipment_count ? 'border-red-500' : 'border-gray-300'}`}
            />
          </div>
          <input
            value={form.type}
            onChange={e => setForm({ ...form, type: e.target.value })}
            onBlur={() => handleBlur('type')}
            placeholder="Tipo do serviço *"
            className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#3B82F6] focus:ring-2 focus:ring-[#3B82F6] bg-white text-[#1F526B] text-base ${touched.type && !form.type ? 'border-red-500' : 'border-gray-300'}`}
          />
          <select value={form.color} onChange={e => setForm({ ...form, color: e.target.value })} className="w-full rounded-lg border-2 px-4 py-2 border-gray-300 bg-white text-[#1F526B]">
            <option value="blue">Azul</option>
            <option value="green">Verde</option>
            <option value="purple">Roxo</option>
            <option value="orange">Laranja</option>
            <option value="red">Vermelho</option>
            <option value="yellow">Amarelo</option>
          </select>
        </div>
        {!isValid && Object.keys(touched).length > 0 && <p className="text-red-500 text-sm mt-2">Preencha todos os campos obrigatórios *</p>}
        <div className="flex gap-3 mt-6">
          <button type="button" onClick={closeAndReset} className="flex-1 py-2 rounded-lg bg-gray-100 text-[#1F526B] font-semibold hover:bg-gray-200 transition">Cancelar</button>
          <button type="submit" disabled={!isValid} className={`flex-1 py-2 rounded-lg bg-[#3B82F6] text-white font-bold hover:bg-[#2563EB] transition ${!isValid ? 'opacity-50 cursor-not-allowed' : ''}`}>{initialData ? 'Atualizar' : 'Adicionar'}</button>
        </div>
      </form>
    </Modal>
  );
}; 