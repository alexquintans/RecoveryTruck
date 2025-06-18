// Utilitários de tipagem para o projeto

// Tipo para funções de atualização de estado do React
declare type SetStateAction<S> = S | ((prevState: S) => S);
declare type Dispatch<A> = (value: A) => void;

// Tipos para eventos do React
declare interface ChangeEvent<T = Element> {
  target: T;
  currentTarget: T;
}

// Tipo para formulários
declare interface FormEvent<T = Element> {
  preventDefault(): void;
  stopPropagation(): void;
  target: T;
  currentTarget: T;
} 