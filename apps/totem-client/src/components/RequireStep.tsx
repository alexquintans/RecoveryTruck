import React from 'react';
import { Navigate } from 'react-router-dom';
import { useTotemStore } from '../store/totemStore';

const stepToRoute: Record<string, string> = {
  welcome: '/',
  service: '/service',
  extras: '/extras',
  customer: '/customer-info',
  terms: '/terms',
  payment: '/payment',
  ticket: '/ticket',
};

export const RequireStep: React.FC<{ step: string; children: React.ReactNode }> = ({ step, children }) => {
  const { currentStep } = useTotemStore();

  if (currentStep === step) return <>{children}</>;

  const route = stepToRoute[currentStep] || '/';
  return <Navigate to={route} replace />;
}; 