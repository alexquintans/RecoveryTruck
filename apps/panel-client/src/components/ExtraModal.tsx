import React, { useState } from 'react';
import { Modal } from './Modal';
import { PlusIcon } from '@heroicons/react/24/solid';

interface ExtraForm {
  name: string;
  description: string;
  price: number;
  stock: number;
  category: string;
  isActive: boolean;
}

interface ExtraModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: Partial<ExtraForm>;
  onSubmit: (data: any) => void;
}

const defaultForm: ExtraForm = {
  name: '',
  description: '',
  price: 0,
  stock: 0,
  category: '',
  isActive: true,
};

export const ExtraModal: React.FC<ExtraModalProps> = ({ isOpen, onClose, initialData, onSubmit }) => {
  const [form, setForm] = useState<ExtraForm>({ ...defaultForm, ...initialData });
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const required = ['name', 'description', 'price', 'stock', 'category'];
  const isValid = required.every(f => {
    const value = form[f as keyof ExtraForm];
    if (f === 'price' || f === 'stock') {
      return value >= 0;
    }
    return String(value).trim() !== '';
  });

  const handleBlur = (field: string) => setTouched(prev => ({ ...prev, [field]: true }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) {
      console.log('Formulário inválido:', form);
      return;
    }
    
    const payload = {
      name: form.name.trim(),
      description: form.description.trim(),
      price: Number(form.price),
      stock: Number(form.stock),
      category: form.category.trim(),
      is_active: form.isActive,
    };
    
    console.log('Payload sendo enviado:', payload);
    
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
      <h2 className="text-2xl font-bold text-[#18446B] mb-6 flex items-center gap-2">
        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#7ED957] text-white">
          <svg width="22" height="22" fill="none" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" stroke="#18446B" strokeWidth="2" strokeLinecap="round"/></svg>
        </span>
        {initialData ? 'Editar Item Extra' : 'Adicionar Item Extra'}
      </h2>
      <form onSubmit={handleSubmit} autoComplete="off">
        <div className="space-y-4">
          <input
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            onBlur={() => handleBlur('name')}
            placeholder="Nome do item *"
            className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#7ED957] focus:ring-2 focus:ring-[#7ED957] bg-white text-[#18446B] text-base ${touched.name && !form.name ? 'border-red-500' : 'border-gray-300'}`}
            autoFocus
          />
          <textarea
            value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })}
            onBlur={() => handleBlur('description')}
            placeholder="Descrição do item *"
            className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#7ED957] focus:ring-2 focus:ring-[#7ED957] bg-white text-[#18446B] text-base ${touched.description && !form.description ? 'border-red-500' : 'border-gray-300'}`}
            rows={2}
          />
          <div className="flex gap-4">
            <input
              type="number"
              value={form.price}
              onChange={e => setForm({ ...form, price: Number(e.target.value) })}
              onBlur={() => handleBlur('price')}
              placeholder="Preço (R$) *"
              className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#7ED957] focus:ring-2 focus:ring-[#7ED957] bg-white text-[#18446B] text-base ${touched.price && form.price < 0 ? 'border-red-500' : 'border-gray-300'}`}
            />
            <input
              type="number"
              value={form.stock}
              onChange={e => setForm({ ...form, stock: Number(e.target.value) })}
              onBlur={() => handleBlur('stock')}
              placeholder="Estoque *"
              className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#7ED957] focus:ring-2 focus:ring-[#7ED957] bg-white text-[#18446B] text-base ${touched.stock && form.stock < 0 ? 'border-red-500' : 'border-gray-300'}`}
            />
          </div>
          <input
            value={form.category}
            onChange={e => setForm({ ...form, category: e.target.value })}
            onBlur={() => handleBlur('category')}
            placeholder="Categoria *"
            className={`w-full rounded-lg border-2 px-4 py-2 transition-all focus:outline-none focus:border-[#7ED957] focus:ring-2 focus:ring-[#7ED957] bg-white text-[#18446B] text-base ${touched.category && !form.category ? 'border-red-500' : 'border-gray-300'}`}
          />
        </div>
        {!isValid && Object.keys(touched).length > 0 && <p className="text-red-500 text-sm mt-2">Preencha todos os campos obrigatórios *</p>}
        <div className="flex gap-3 mt-6">
          <button type="button" onClick={closeAndReset} className="flex-1 py-2 rounded-lg bg-gray-100 text-[#18446B] font-semibold hover:bg-gray-200 transition">Cancelar</button>
          <button type="submit" disabled={!isValid} className={`flex-1 py-2 rounded-lg bg-[#7ED957] text-[#18446B] font-bold hover:bg-[#5fcf3a] transition ${!isValid ? 'opacity-50 cursor-not-allowed' : ''}`}>{initialData ? 'Atualizar' : 'Adicionar'}</button>
        </div>
      </form>
    </Modal>
  );
}; 