import { enTranslations } from './en';
import { ptTranslations } from './pt';
import { arTranslations } from './ar';

export type TranslationKey = keyof typeof enTranslations;
export type NestedTranslationKey<T extends TranslationKey> =
  keyof (typeof enTranslations)[T];

export type LanguageCode = 'en' | 'pt' | 'ar';

export const translations = {
  en: enTranslations,
  pt: ptTranslations,
  ar: arTranslations,
};

export const languageNames = {
  en: '🇬🇧 English',
  pt: '🇧🇷 Português',
  ar: '🇸🇦 العربية',
};

export const rtlLanguages: LanguageCode[] = ['ar'];

export const isRtlLanguage = (lang: LanguageCode): boolean =>
  rtlLanguages.includes(lang);
