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
// import {
//   FileUploadList,
//   FileUploadRoot,
//   FileUploadTrigger,
// } from "../components/ui/file-upload";

const DotLottieReact = dynamic(
  () =>
    import("@lottiefiles/dotlottie-react").then((mod) => mod.DotLottieReact),
  { ssr: false }
);

export default function Home() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [isProcessingPdf, setIsProcessingPdf] = useState(false);
  const [text, setText] = useState("");
  const [shouldAttachFile, setShouldAttachFile] = useState(false);

  const [dotPositions, setDotPositions] = useState<DotPositions>([]);
  const [currPage, setCurrPage] = useState(0);
  const [isPrinting, setIsPrinting] = useState(false);

  const submitText = async () => {
    setIsProcessingPdf(true);
    try {
      const formData = new FormData();
      formData.append("type", "text");
      formData.append("text", text);
      const response = await fetch("http://localhost:6969", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        toaster.success({
          title: "Success",
          description: "Text transcribed successfully!",
        });
        const braillePositions: DotPositions = await response.json();
        setDotPositions(braillePositions);
        setCurrPage(0);
      } else {
        toaster.error({
          title: "Error",
          description: "Failed to transcribe text.",
        });
      }
    } catch {
      toaster.error({
        title: "Error",
        description: "An unexpected error occurred while sending text.",
      });
    } finally {
      setIsProcessingPdf(false);
    }
  };

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
        setDotPositions(braillePositions);
        setCurrPage(0);
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

  async function printCurrentPage() {
    if (!dotPositions[currPage]) return;
    setIsPrinting(true);
    try {
      const response = await fetch("http://localhost:6969/print_dots", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dotPositions: dotPositions[currPage] }),
      });
      if (response.ok) {
        toaster.success({
          title: "Printing",
          description: `Page ${currPage + 1} is printing...`,
        });
      } else {
        toaster.error({ title: "Error", description: "Failed to print." });
      }
    } catch {
      toaster.error({
        title: "Error",
        description: "Something went wrong while printing.",
      });
    } finally {
      setIsPrinting(false);
    }
  }

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

      {dotPositions.length === 0 && (
        <VStack w="100%" p={3}>
          <Text fontSize="xl">Enter text to get started</Text>
          <Input
            placeholder="Enter text here"
            onChange={(e) => setText(e.target.value)}
          />
          <HStack>
            <Button
              onClick={() => {
                submitPdf();
              }}
              disabled={isProcessingPdf}
              variant="outline"
            >
              Attach File
            </Button>
            <Button onClick={submitText} disabled={isProcessingPdf}>
              Submit Text
            </Button>
          </HStack>
          <Input
            type="file"
            accept=".pdf"
            onChange={(e) => {
              if (e.target.files) {
                setPdfFile(e.target.files[0]);
              }
            }}
          />
          {isProcessingPdf && (
            <HStack mt={2}>
              <Spinner size="sm" />
              <Text>Processing...</Text>
            </HStack>
          )}
        </VStack>
      )}

      {dotPositions.length !== 0 && (
        <VStack w="100%" p={3}>
          <PDFPreview page={currPage} dotPositions={dotPositions} />
          <HStack>
            <Button
              onClick={async () => {
                await printCurrentPage();
                setCurrPage((p) => Math.min(dotPositions.length - 1, p + 1));
              }}
              disabled={currPage >= dotPositions.length || isPrinting}
            >
              Print and proceed to next page
            </Button>
            <Button
              color="red.400"
              onClick={() => {
                fetch("http://localhost:6969/stop_print", {
                  method: "POST",
                });
              }}
            >
              STOP
            </Button>
            <Button
              onClick={() => {
                fetch("http://localhost:6969/pause_print", {
                  method: "POST",
                });
              }}
            >
              PAUSE
            </Button>
            <Button
              color="green"
              onClick={() => {
                fetch("http://localhost:6969/resume_print", {
                  method: "POST",
                });
              }}
            >
              RESUME
            </Button>
          </HStack>
        </VStack>
      )}
    </VStack>
  );
}
