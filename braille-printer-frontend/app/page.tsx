"use client";
import { useState } from "react";
import { Heading, HStack, Text, VStack, Input, Button } from "@chakra-ui/react";
import { toaster, Toaster } from "../components/ui/toaster";
// import { DotLottieReact } from "@lottiefiles/dotlottie-react";
import dynamic from 'next/dynamic';


const DotLottieReact = dynamic(
  () =>
    import('@lottiefiles/dotlottie-react').then((mod) => mod.DotLottieReact),
  { ssr: false }
);

export default function Home() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [textValue, setTextValue] = useState("");

  const submitPdf = async () => {
    if (!pdfFile) return;
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
          description: "PDF file sent successfully!",
        });
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
    }
  };

  const submitText = async () => {
    if (!textValue) return;
    try {
      const response = await fetch("http://localhost:6969", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "text", payload: textValue }),
      });
      if (response.ok) {
        toaster.success({
          title: "Success",
          description: "Text sent successfully!",
        });
      } else {
        toaster.error({
          title: "Error",
          description: "Failed to send text.",
        });
      }
    } catch {
      toaster.error({
        title: "Error",
        description: "An unexpected error occurred while sending text.",
      });
    }
  };

  return (
    <VStack alignContent="center" p={3}>
      <Toaster/>
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
        <Button onClick={submitPdf}>Submit PDF</Button>

        <Text fontSize="xl">Or submit plain text</Text>
        <Input
          placeholder="Type something..."
          value={textValue}
          onChange={(e) => setTextValue(e.target.value)}
        />
        <Button onClick={submitText}>Submit Text</Button>
      </VStack>
    </VStack>
  );
}
