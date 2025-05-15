import { Toaster } from 'sonner';
import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import { ConnectWalletButton } from '@/components/ConnectWalletButton';
// import { ThemeProvider } from '@/components/theme-provider'; // Removed, will add back if/when needed

import './globals.css';
// SessionProvider is likely not needed as we removed next-auth
// import { SessionProvider } from 'next-auth/react';

export const metadata: Metadata = {
  metadataBase: new URL('http://localhost:3000'), // Placeholder, update when domain is known
  title: 'AlgoFOMO - Algorand Avatar Battles',
  description:
    'Bet ALGO, cast spells, and watch Twitter avatars battle for momentum in AlgoFOMO!',
};

export const viewport = {
  maximumScale: 1, // Disable auto-zoom on mobile Safari
};

const geist = Geist({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-geist',
});

const geistMono = Geist_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-geist-mono',
});

// Theme color script can be kept if we plan to implement light/dark mode later via CSS only or a new simple provider
const LIGHT_THEME_COLOR = 'hsl(0 0% 100%)';
const DARK_THEME_COLOR = 'hsl(240deg 10% 3.92%)';
const THEME_COLOR_SCRIPT = `\
(function() {
  var html = document.documentElement;
  var meta = document.querySelector('meta[name="theme-color"]');
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute('name', 'theme-color');
    document.head.appendChild(meta);
  }
  function updateThemeColor() {
    var isDark = html.classList.contains('dark'); // This assumes a 'dark' class is manually/CSS managed
    meta.setAttribute('content', isDark ? '${DARK_THEME_COLOR}' : '${LIGHT_THEME_COLOR}');
  }
  var observer = new MutationObserver(updateThemeColor);
  observer.observe(html, { attributes: true, attributeFilter: ['class'] });
  updateThemeColor();
})();`;

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      // `next-themes` injects an extra classname to the body element to avoid
      // visual flicker before hydration. Hence the `suppressHydrationWarning`
      // prop is necessary to avoid the React hydration mismatch warning.
      // https://github.com/pacocoursey/next-themes?tab=readme-ov-file#with-app
      suppressHydrationWarning
      className={`${geist.variable} ${geistMono.variable}`}
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: THEME_COLOR_SCRIPT,
          }}
        />
      </head>
      <body className="antialiased">
        <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-14 max-w-screen-2xl items-center justify-between">
            <div className="mr-4 hidden md:flex">
              {/* Placeholder for Logo/Brand */}
              <a className="mr-6 flex items-center space-x-2" href="/">
                <span className="hidden font-bold sm:inline-block">
                  AlgoFOMO
                </span>
              </a>
            </div>
            <div className="flex items-center space-x-2">
              <ConnectWalletButton />
            </div>
          </div>
        </header>
        <Toaster position="top-center" />
        {/* SessionProvider removed, children directly rendered */}
        {children}
        {/* </ThemeProvider> */}
      </body>
    </html>
  );
}
