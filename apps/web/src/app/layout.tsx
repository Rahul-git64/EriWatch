import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EriWatch | Satellite Early Warning & Grievance Platform for Village Tanks",
  description:
    "Monitoring water spread, 30-day hydrological forecasts, and grounded legal petitions for Tamil Nadu village irrigation tanks (eris).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
