'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import {
  translations,
  LanguageCode,
  TranslationKey,
  NestedTranslationKey,
  isRtlLanguage,
} from '@/utils/translations';

type LanguageContextType = {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  isRtl: boolean;
  t: <T extends TranslationKey>(section: T, key: NestedTranslationKey<T>) => string;
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

type LanguageProviderProps = {
  children: ReactNode;
};

const SUPPORTED_LANGUAGES: LanguageCode[] = ['en', 'pt', 'ar'];

const applyDocumentDirection = (lang: LanguageCode) => {
  if (typeof document === 'undefined') return;
  const dir = isRtlLanguage(lang) ? 'rtl' : 'ltr';
  document.documentElement.setAttribute('dir', dir);
  document.documentElement.setAttribute('lang', lang);
};

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [language, setLanguageState] = useState<LanguageCode>('pt'); // Default to Portuguese

  useEffect(() => {
    // Load saved language preference from localStorage if available
    const savedLanguage = localStorage.getItem('language') as LanguageCode | null;
    if (savedLanguage && SUPPORTED_LANGUAGES.includes(savedLanguage)) {
      setLanguageState(savedLanguage);
      applyDocumentDirection(savedLanguage);
      return;
    }
    // Auto-detect from browser language
    const browserLang = navigator.language?.toLowerCase() || '';
    let detected: LanguageCode = 'en';
    if (browserLang.startsWith('pt')) {
      detected = 'pt';
    } else if (browserLang.startsWith('ar')) {
      detected = 'ar';
    }
    setLanguageState(detected);
    applyDocumentDirection(detected);
  }, []);

  const setLanguage = (lang: LanguageCode) => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);
    applyDocumentDirection(lang);
  };

  // Translation function
  const t = <T extends TranslationKey>(section: T, key: NestedTranslationKey<T>): string => {
    // Type assertion to avoid index signature error
    const sectionTranslations = translations[language][section] as Record<string, string>;
    return sectionTranslations[key as string] || `${String(section)}.${String(key)}`;
  };

  return (
    <LanguageContext.Provider
      value={{ language, setLanguage, isRtl: isRtlLanguage(language), t }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
