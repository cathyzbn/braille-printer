"use client";
import { useState } from "react";
import { Heading, HStack, Text, VStack, Input, Button } from "@chakra-ui/react";
import { DotLottieReact } from "@lottiefiles/dotlottie-react";

export default function Home() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [textValue, setTextValue] = useState("");

  const submitPdf = async () => {
    if (!pdfFile) return;
    const formData = new FormData();
    formData.append("file", pdfFile);
    await fetch("http://localhost:6969", {
      method: "POST",
      body: formData,
    });
  };

  const submitText = async () => {
    if (!textValue) return;
    await fetch("http://localhost:6969", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "text", payload: textValue }),
    });
  };

  return (
    <VStack alignContent="center" p={3}>
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
