import React from 'react';

interface Service {
  id: string;
  name: string;
  description?: string;
  price?: number;
  duration_minutes: number;
  is_active: boolean;
}
interface Extra {
  id: string;
  name: string;
  description?: string;
  price?: number;
  stock: number;
  is_active: boolean;
}
interface Props {
  services: Service[];
  extras: Extra[];
  toggleService: (id: string, enable: boolean, duration?: number) => void;
  toggleExtra: (id: string, enable: boolean, stock?: number) => void;
  onContinue: () => void;
}

export const OperatorConfigStep: React.FC<Props> = ({ services, extras, toggleService, toggleExtra, onContinue }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Serviços Disponíveis</h2>
      <div className="grid gap-4">
        {services.map((svc) => (
          <div key={svc.id} className={`border rounded p-4 ${svc.is_active ? 'bg-green-50' : 'bg-gray-50'}`}>
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-lg">{svc.name}</h3>
                {svc.description && <p className="text-sm text-gray-600">{svc.description}</p>}
                {svc.price !== undefined && (
                  <p className="text-sm text-gray-700 mt-1">R$ {svc.price.toFixed(2)}</p>
                )}
              </div>
              <label className="inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={svc.is_active}
                  onChange={(e) => toggleService(svc.id, e.target.checked)}
                />
                <div
                  className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-offset-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:bg-blue-600 transition-all"
                />
              </label>
            </div>
            <div className="mt-3 flex items-center gap-2">
              <span className="text-sm mr-2">Duração (min)</span>
              <input
                type="number"
                value={svc.duration_minutes}
                onChange={(e) => toggleService(svc.id, svc.is_active, parseInt(e.target.value) || 1)}
                className="w-20 border rounded px-2 py-1 text-sm"
                min={1}
              />
            </div>
          </div>
        ))}
      </div>

      <h2 className="text-xl font-semibold mt-8">Itens Extras Disponíveis</h2>
      <div className="grid md:grid-cols-2 gap-4">
        {extras.map((ex) => (
          <div key={ex.id} className={`border rounded p-4 ${ex.is_active ? 'bg-green-50' : 'bg-gray-50'}`}>
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-lg">{ex.name}</h3>
                {ex.description && <p className="text-sm text-gray-600">{ex.description}</p>}
                {ex.price !== undefined && <p className="text-sm text-gray-700 mt-1">R$ {ex.price.toFixed(2)}</p>}
              </div>
              <label className="inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={ex.is_active}
                  onChange={(e) => toggleExtra(ex.id, e.target.checked)}
                />
                <div
                  className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-offset-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:bg-blue-600 transition-all"
                />
              </label>
            </div>
            <div className="mt-3 flex items-center gap-2">
              <span className="text-sm mr-2">Estoque</span>
              <input
                type="number"
                value={ex.stock}
                onChange={(e) => toggleExtra(ex.id, ex.is_active, parseInt(e.target.value) || 0)}
                className="w-20 border rounded px-2 py-1 text-sm"
                min={0}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="pt-4">
        <button
          type="button"
          onClick={onContinue}
          className="px-6 py-3 bg-primary text-white font-semibold rounded-md hover:bg-primary/80 transition-colors"
        >
          Continuar
        </button>
      </div>
    </div>
  );
}; 