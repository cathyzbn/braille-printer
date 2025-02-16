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
import { PDFPreview } from "../components/ui/pdf-preview";
import dynamic from "next/dynamic";

const DotLottieReact = dynamic(
  () =>
    import("@lottiefiles/dotlottie-react").then((mod) => mod.DotLottieReact),
  { ssr: false }
);

export default function Home() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [isProcessingPdf, setIsProcessingPdf] = useState(false);
  const [dotPositions, setActiveDotPositions] = useState({}); // no type checking rn
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
        // const blob = await response.blob();
        // const url = URL.createObjectURL(blob);
        toaster.success({
          title: "Success",
          description: "PDF file transcribed successfully!",
        });
        const braillePositions = await response.json();
        setActiveDotPositions(braillePositions);
        setCurrPage(1);
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

  // const submitText = async () => {
  //   if (!textValue) return;
  //   try {
  //     const response = await fetch("http://localhost:6969", {
  //       method: "POST",
  //       headers: { "Content-Type": "application/json" },
  //       body: JSON.stringify({ type: "text", payload: textValue }),
  //     });
  //     if (response.ok) {
  //       toaster.success({
  //         title: "Success",
  //         description: "Text sent successfully!",
  //       });
  //     } else {
  //       toaster.error({
  //         title: "Error",
  //         description: "Failed to send text.",
  //       });
  //     }
  //   } catch {
  //     toaster.error({
  //       title: "Error",
  //       description: "An unexpected error occurred while sending text.",
  //     });
  //   }
  // };

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
      {/* don't render below if we've received dot_positions */}
      {Object.keys(dotPositions).length === 0 && (
        <VStack w="100%" p={3}>
          <Text fontSize="xl">Upload a PDF file to get started</Text>
          <Input
            type="file"
            onChange={(e) => {
              if (e.target.files) {
                setPdfFile(e.target.files[0]);
              }
            }}
            accept=".pdf"
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
          <VStack id="braille-pdf-container"></VStack>
        </VStack>
      )}
      {Object.keys(dotPositions).length !== 0 && (
        <VStack w="100%" p={3}>
          <PDFPreview page={currPage} />
          <Button
            onClick={() => setCurrPage(currPage + 1)}
            disabled={currPage === 0}
          >
            Print
          </Button>
        </VStack>
      )}
    </VStack>
  );
}
