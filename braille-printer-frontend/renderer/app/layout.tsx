import { Provider } from "../components/ui/provider";
import { Literata, Mulish } from "next/font/google";

const literata = Literata({
  variable: "--font-literata",
  subsets: ["latin"],
});

const mulish = Mulish({
  variable: "--font-mulish",
  subsets: ["latin"],
  weight: "400",
});

export default function RootLayout(props: { children: React.ReactNode }) {
  const { children } = props;
  return (
    <html
      className={`${literata.variable} ${mulish.variable}`}
      suppressHydrationWarning
    >
      <body>
        <Provider>{children}</Provider>
      </body>
    </html>
  );
}
