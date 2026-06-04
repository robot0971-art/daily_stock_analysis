export type UiLanguage = 'ko' | 'en';

export const DEFAULT_UI_LANGUAGE: UiLanguage = 'ko';
export const SUPPORTED_UI_LANGUAGES: readonly UiLanguage[] = ['ko', 'en'];

const TITLE_BY_LANGUAGE: Record<UiLanguage, string> = {
  ko: 'DSA 주식 분석',
  en: 'DSA Stock Analysis',
};

export function applyDocumentUiLanguage(language: UiLanguage = DEFAULT_UI_LANGUAGE): void {
  document.documentElement.lang = language;
  document.title = TITLE_BY_LANGUAGE[language];
}
