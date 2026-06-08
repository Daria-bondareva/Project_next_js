import "./globals.css";
import styles from "./layout.module.css";
import { Inter } from "next/font/google";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import type { Metadata } from "next";

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Kindred",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uk" className={inter.variable}>
      <body>
        <Header />
        <main className={styles.main}>
          <div className={styles.container}>
            {children}
          </div>
        </main>
        <Footer />
      </body>
    </html>
  );
}
