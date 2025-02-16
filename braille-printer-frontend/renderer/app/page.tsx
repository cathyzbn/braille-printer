// ------------------------------------
// page.tsx
// ------------------------------------
"use client";
import { useEffect, useState } from "react";
import {
  Heading,
  HStack,
  Text,
  VStack,
  Input,
  Button,
  Spinner,
} from "@chakra-ui/react";
import { toaster, Toaster } from "../components/ui/toaster";
import { PDFPreview, DotPositions } from "../components/ui/pdf-preview";
import dynamic from "next/dynamic";

const DotLottieReact = dynamic(
  () => import("@lottiefiles/dotlottie-react").then((mod) => mod.DotLottieReact),
  { ssr: false }
);

export default function Home() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [isProcessingPdf, setIsProcessingPdf] = useState(false);

  // Holds an array of pages, where each page is an array of DotPosition
  const [dotPositions, setDotPositions] = useState<DotPositions>([]);
  // Active page
  const [currPage, setCurrPage] = useState(0);

  const submitPdf = async () => {
    if (!pdfFile) return;
    setIsProcessingPdf(true);
    try {
      const formData = new FormData();
      formData.append("file", pdfFile);
      formData.append("type", "pdf");
      const response = await fetch("http://localhost:6969", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        toaster.success({
          title: "Success",
          description: "PDF file transcribed successfully!",
        });
        const braillePositions: DotPositions = await response.json();
        // braillePositions => array of pages => each page is array of DotPosition
        setDotPositions(braillePositions);
        setCurrPage(0); // start at page 0
      } else {
        toaster.error({
          title: "Error",
          description: "Failed to send PDF file.",
        });
      }
    } catch {
      toaster.error({
        title: "Error",
        description: "An unexpected error occurred while sending PDF file.",
      });
    } finally {
      setIsProcessingPdf(false);
    }
  };

  useEffect(() => {
    window.electronAPI?.setTitle("Braille Printer");
  }, []);

  return (
    <VStack alignContent="center" p={3}>
      <Toaster />
      <VStack borderBottom="1px solid" borderColor="gray.300" w="100%" p={3}>
        <HStack>
          <Heading fontSize="5xl">Braille Printer</Heading>
        </HStack>
        <HStack>
          <Text fontSize="2xl">Any PDF to printed braille</Text>
        </HStack>
      </VStack>

      <DotLottieReact
        src="./printer.lottie"
        loop
        autoplay
        style={{ width: "400px", height: "200px" }}
      />

      {/* If we have no dot positions, show the upload */}
      {dotPositions.length === 0 && (
        <VStack w="100%" p={3}>
          <Text fontSize="xl">Upload a PDF file to get started</Text>
          <Input
            type="file"
            accept=".pdf"
            onChange={(e) => {
              if (e.target.files) {
                setPdfFile(e.target.files[0]);
              }
            }}
          />
          <Button onClick={submitPdf} disabled={isProcessingPdf}>
            Submit PDF
          </Button>
          {isProcessingPdf && (
            <HStack mt={2}>
              <Spinner size="sm" />
              <Text>Processing...</Text>
            </HStack>
          )}
        </VStack>
      )}

      {/* If we have dotPositions, show the PDF preview + controls */}
      {dotPositions.length !== 0 && (
        <VStack w="100%" p={3}>
          <PDFPreview page={currPage} dotPositions={dotPositions} />
          <HStack>
            <Button
              onClick={() =>
                setCurrPage(Math.min(dotPositions.length - 1, currPage + 1))
              }
              disabled={currPage >= dotPositions.length - 1}
            >
              Print and proceed to next page
            </Button>
          </HStack>
        </VStack>
      )}
    </VStack>
  );
}
