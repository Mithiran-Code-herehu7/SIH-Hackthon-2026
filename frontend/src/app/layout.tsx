import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Agentic AI Workbench | Private On-Premise Assistant',
  description: 'Editorial, secure, offline AI assistant for refineries, PSUs, and defense installations. SIH26117.',
  icons: {
    icon: '/icon.png',
    shortcut: '/favicon.ico',
    apple: '/icon.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#F5F2EB] text-[#1C1B24] font-sans selection:bg-[#2C2B5B] selection:text-white">
        {children}
      </body>
    </html>
  );
}
