"use client";
import { useEffect, useState } from "react";
import {
  Heading,
  HStack,
  Text,
  VStack,
  Button,
  Textarea,
  Spinner,
  Icon,
} from "@chakra-ui/react";

import { toaster, Toaster } from "../components/ui/toaster";
import { DotPositions } from "../components/ui/pdf-preview";
import { PDFLive } from "../components/ui/pdf-live";
import dynamic from "next/dynamic";
import { Connector } from "../components/connector";
import { fetchApi } from "../utils/api";
import {
  FileUploadList,
  FileUploadRoot,
  FileUploadTrigger,
} from "../components/ui/file-upload";

const FaStop = dynamic(
  () => import("react-icons/fa").then((mod) => mod.FaStop),
  { ssr: false }
);
const FaPlay = dynamic(
  () => import("react-icons/fa").then((mod) => mod.FaPlay),
  { ssr: false }
);
const FaPause = dynamic(
  () => import("react-icons/fa").then((mod) => mod.FaPause),
  { ssr: false }
);

const DotLottieReact = dynamic(
  () =>
    import("@lottiefiles/dotlottie-react").then((mod) => mod.DotLottieReact),
  { ssr: false }
);

export default function Home() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [isProcessingPdf, setIsProcessingPdf] = useState(false);
  const [text, setText] = useState("");
  const [dotPositions, setDotPositions] = useState<DotPositions>([]);
  const [currPage, setCurrPage] = useState(0);
  const [isPrinting, setIsPrinting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const submitText = async () => {
    if (!text.trim()) return;
    const formData = new FormData();
    formData.append("type", "text");
    formData.append("text", text);
    setIsProcessingPdf(true);
    const response = await fetchApi("/", {
      method: "POST",
      body: formData,
    });
    if (response) {
      toaster.success({
        title: "Success",
        description: "Text transcribed successfully!",
      });
      const braillePositions: DotPositions = await response.json();
      setDotPositions(braillePositions);
      setCurrPage(0);
    }
    setIsProcessingPdf(false);
  };

  const submitPdf = async () => {
    if (!pdfFile) return;
    setIsProcessingPdf(true);
    const formData = new FormData();
    formData.append("file", pdfFile);
    formData.append("type", "pdf");
    const response = await fetchApi("/", {
      method: "POST",
      body: formData,
    });
    if (response) {
      toaster.success({
        title: "Success",
        description: "PDF file transcribed successfully!",
      });
      const braillePositions: DotPositions = await response.json();
      setDotPositions(braillePositions);
      setCurrPage(0);
    }
    setIsProcessingPdf(false);
  };

  async function printCurrentPage() {
    if (!dotPositions[currPage]) return;
    setIsPrinting(true);
    const response = await fetchApi("/print_dots", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dotPositions: dotPositions[currPage] }),
    });
    if (response) {
      toaster.success({
        title: "Printing",
        description: `Page ${currPage + 1} is printing...`,
      });
    }
    setIsPrinting(false);
  }

  useEffect(() => {
    window.electronAPI?.setTitle("Braille Printer");
  }, []);

  return (
    <VStack alignContent="center" p={3}>
      <Toaster />
      <VStack
        borderBottom="1px solid"
        borderColor="gray.300"
        w="100%"
        p={5}
        gapY={5}
      >
        <HStack>
          <Heading fontSize="6xl">Braille Printer</Heading>
        </HStack>
        <HStack>
          <Text fontSize="2xl">Any PDF to printed braille</Text>
        </HStack>
      </VStack>

      <Connector isConnected={isConnected} setIsConnected={setIsConnected} />

      {dotPositions.length === 0 && (
        <DotLottieReact
          src="./printer.lottie"
          loop
          autoplay
          style={{ width: "400px", height: "200px" }}
        />
      )}

      {isConnected && dotPositions.length === 0 && (
        <VStack w="80%" p={3}>
          <Text fontSize="xl">Enter text or upload a PDF</Text>

          {/* TEXT INPUT (disabled if a PDF is already chosen) */}
          <Textarea
            placeholder="Enter text here"
            value={text}
            onChange={(e) => {
              setText(e.target.value);
              if (e.target.value) {
                // if user starts typing, remove any selected PDF
                setPdfFile(null);
              }
            }}
            disabled={!!pdfFile}
          />

          {/* SUBMIT BUTTONS */}
          <HStack w="100%" alignItems="start" justifyContent="flex-end">
            <FileUploadRoot
              accept=".pdf"
              onChange={(event) => {
                const files = (event.target as HTMLInputElement).files;
                if (files && files.length > 0) {
                  setPdfFile(files[0]);
                  setText(""); // if user chooses a PDF, clear any typed text
                }
              }}
            >
              <FileUploadTrigger asChild>
                <Button
                  variant="outline"
                  disabled={isProcessingPdf || !!text}
                  // leftIcon={<HiUpload />}
                >
                  Attach File
                </Button>
              </FileUploadTrigger>
              <FileUploadList />
            </FileUploadRoot>
            <Button
              onClick={() => {
                if (text.trim()) {
                  submitText();
                } else {
                  submitPdf();
                }
              }}
            >
              Submit
            </Button>
          </HStack>

          {isProcessingPdf && (
            <HStack mt={2}>
              <Spinner size="sm" />
              <Text>Processing...</Text>
            </HStack>
          )}
        </VStack>
      )}

      {isConnected && dotPositions.length !== 0 && (
        <VStack w="50%" p={3}>
          <HStack justifyContent="space-between" w="100%">
            <Button
              onClick={() => {
                setCurrPage((p) => Math.max(0, p - 1));
              }}
              disabled={currPage <= 0}
              variant="outline"
            >
              Previous
            </Button>

            <Text>Page {currPage + 1}</Text>
            {currPage < dotPositions.length - 1 ? (
              <Button
                onClick={() => {
                  setCurrPage((p) => Math.min(dotPositions.length - 1, p + 1));
                }}
              disabled={currPage >= dotPositions.length - 1}
              variant="outline"
            >
                Next
              </Button>
            ) : (
              <Button
                onClick={() => {
                  setDotPositions([]);
                }}
                variant="outline"
              >
                Exit
              </Button>
            )}
          </HStack>
          <PDFLive page={currPage} dotPositions={dotPositions} />
          <HStack>
            <Button
              onClick={async () => {
                await printCurrentPage();
              }}
              disabled={currPage >= dotPositions.length || isPrinting}
            >
              Print
            </Button>
            <Button
              color="red.400"
              onClick={() => {
                fetchApi("/stop_print", {
                  method: "POST",
                });
              }}
            >
              <Icon as={FaStop} />
              STOP
            </Button>
            <Button
              onClick={() => {
                fetchApi("/pause_print", {
                  method: "POST",
                });
              }}
            >
              <Icon as={FaPause}  />
              PAUSE
            </Button>
            <Button
              color="green"
              onClick={() => {
                fetchApi("/resume_print", {
                  method: "POST",
                });
              }}
            >
              <Icon as={FaPlay} />
              RESUME
            </Button>
          </HStack>
        </VStack>
      )}
    </VStack>
  );
}
