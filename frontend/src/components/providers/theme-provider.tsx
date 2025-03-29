// components/providers/theme-provider.tsx
"use client"; // This component needs to be a Client Component

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import type { ThemeProviderProps } from "next-themes";

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  // Pass all props down to the actual provider from next-themes
  // Wrap the children of your app with it
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
