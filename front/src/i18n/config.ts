import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslation from './locales/en.json';
import zhTranslation from './locales/zh.json';

type RecursiveKeyOf<TObj extends object> = {
  [TKey in keyof TObj & (string | number)]: TObj[TKey] extends object
    ? `${TKey}` | `${TKey}.${RecursiveKeyOf<TObj[TKey]>}`
    : `${TKey}`
}[keyof TObj & (string | number)];

// Define the structure of translation parameters
type TranslationParams = {
  value?: string | number;
  [key: string]: any;
};

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'translation';
    resources: {
      translation: typeof enTranslation;
    };
    returnNull: false;
    keySeparator: '.';
    nsSeparator: false;
    // Add support for translation parameters
    tFunctionParams: TranslationParams;
  }
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: enTranslation,
      },
      zh: {
        translation: zhTranslation,
      },
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export type TranslationKey = RecursiveKeyOf<typeof enTranslation>;
export default i18n; 