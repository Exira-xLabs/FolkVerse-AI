"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { dictionaries, type Locale } from "@/lib/i18n";

const LocaleContext = createContext<{ locale: Locale; setLocale: (locale: Locale) => void }>({
  locale: "en", setLocale: () => {},
});

export function LocaleProvider({ children, initialLocale }: { children: React.ReactNode; initialLocale: Locale }) {
  const [locale, setLocale] = useState<Locale>(initialLocale);
  useEffect(() => {
    document.documentElement.lang = locale;
    document.cookie = `folkverse_locale=${locale}; Path=/; Max-Age=31536000; SameSite=Lax`;
  }, [locale]);
  return <LocaleContext.Provider value={{ locale, setLocale }}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const context = useContext(LocaleContext);
  return { ...context, t: dictionaries[context.locale] };
}
