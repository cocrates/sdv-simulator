/**
 * React i18n hook (ASR-020). Provides `t(key)` and the current `lang` plus a
 * `setLang` switch. Initial language follows the catalog precedence in
 * messages.ts: user switch choice > server-injected lang > browser locale > ko.
 */

import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { catalogs, persistLang, resolveInitialLang } from "./messages";
import type { Lang, MessageKey } from "./messages";

interface I18nContextValue {
  lang: Lang;
  /**
   * Translate a message key in the current language. `{name}` placeholders
   * in the catalog entry are replaced from `params` (e.g. `editor.errorsCount`
   * with `{ n: 3 }`).
   */
  t: (key: MessageKey, params?: Record<string, string | number>) => string;
  /** Switch UI language and persist the choice (spec requires a ko/en switch). */
  setLang: (lang: Lang) => void;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => resolveInitialLang());

  const setLang = useCallback((next: Lang) => {
    persistLang(next);
    setLangState(next);
  }, []);

  const value = useMemo<I18nContextValue>(
    () => ({
      lang,
      t: (key, params) => {
        let text = catalogs[lang][key];
        if (params) {
          for (const [name, val] of Object.entries(params)) {
            text = text.replace(`{${name}}`, String(val));
          }
        }
        return text;
      },
      setLang,
    }),
    [lang, setLang],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within an I18nProvider");
  return ctx;
}
