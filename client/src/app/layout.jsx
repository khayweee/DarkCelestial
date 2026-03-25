import './globals.css';

export const metadata = {
  title: 'Trading Assistant Dashboard',
  description: 'Real-time entry & exit points across Crypto and NYSE markets',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
