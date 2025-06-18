declare namespace React {
  export type FC<P = {}> = (props: P) => any;
  export type ReactNode = any;
  export type FormEvent<T = any> = any;
  export type ChangeEvent<T = any> = any;
  export type ButtonHTMLAttributes<T = any> = any;
  export type Context<T> = any;
}

declare module 'react' {
  export const React: typeof React;
  export default React;
  
  // Hooks
  export const useState: <T>(initialState: T | (() => T)) => [T, (newState: T | ((prevState: T) => T)) => void];
  export const useEffect: (effect: () => void | (() => void), deps?: any[]) => void;
  export const useRef: <T>(initialValue: T) => { current: T };
  export const useCallback: <T extends (...args: any[]) => any>(callback: T, deps: any[]) => T;
  export const useMemo: <T>(factory: () => T, deps: any[]) => T;
  export const useContext: <T>(context: React.Context<T>) => T;
  
  // Re-export tipos do namespace
  export type FC<P = {}> = React.FC<P>;
  export type ReactNode = React.ReactNode;
  export type FormEvent<T = any> = React.FormEvent<T>;
  export type ChangeEvent<T = any> = React.ChangeEvent<T>;
  export type ButtonHTMLAttributes<T = any> = React.ButtonHTMLAttributes<T>;
}

declare module 'react-dom' {
  import * as ReactDOM from 'react-dom';
  export = ReactDOM;
  export as namespace ReactDOM;
}

declare module 'react-router-dom' {
  export const BrowserRouter: any;
  export const Routes: any;
  export const Route: any;
  export const Navigate: any;
  export const useNavigate: any;
  export const Outlet: any;
}

declare module 'framer-motion' {
  export const motion: any;
  export const AnimatePresence: any;
}

declare module '@tanstack/react-query' {
  export const useQuery: any;
  export const QueryClient: any;
  export const QueryClientProvider: any;
} 