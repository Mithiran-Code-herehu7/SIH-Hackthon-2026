import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Agentic AI Workbench | Private On-Premise Assistant',
  description: 'Editorial, secure, offline AI assistant for refineries, PSUs, and defense installations. SIH26117.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#F7F5F2] text-[#111318] font-sans selection:bg-[#312E81] selection:text-white">
        {children}
      </body>
    </html>
  );
}
