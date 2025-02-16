// ------------------------------------
// pdf-preview.tsx
// ------------------------------------
import React, { useEffect, useState } from "react";
import { VStack, Text } from "@chakra-ui/react";
import { fetchApi } from "../../utils/api";

// Each object in your Python code is:
// {"x": float, "y": float, "punch": bool, "page": int}
export interface DotPosition {
  x: number;
  y: number;
  punch: boolean;
  page: number;
}

// The Python code returns: DotPosition[][] (array of pages)
export type DotPositions = DotPosition[][];

export interface PDFPreviewProps {
  // Which page do we want to preview?
  page: number;
  // The entire array-of-arrays of dot positions
  dotPositions: DotPositions;
}

export const PDFPreview: React.FC<PDFPreviewProps> = ({ page, dotPositions }) => {
  // This holds the PDF we fetch back from your server
  const [pdfFile, setPdfFile] = useState<Blob | null>(null);

  useEffect(() => {
    if (dotPositions.length === 0) return;
    // Make sure we don’t go out of bounds
    if (page < 0 || page >= dotPositions.length) return;

    // For demonstration, we pass just the page we want
    fetchPdf(dotPositions[page]);
  }, [page, dotPositions]);

  // This requests a PDF from the server by POSTing just the dotPositions for that page
  async function fetchPdf(pageDotPositions: DotPosition[]) {
    const response = await fetchApi("/dot_pos_to_pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dotPositions: pageDotPositions }),
    });

    if (response) {
      const blob = await response.blob();
      setPdfFile(blob);
    }
  }

  return (
    <VStack outline="1px solid" outlineColor="gray.800" pt={2} borderRadius="md" width="100%" height="65vh" maxWidth="860px">
      {pdfFile && (
        <object
          data={`${URL.createObjectURL(pdfFile)}#toolbar=0&navpanes=0`}
          type="application/pdf"
          width="100%"
          height="100%"
        >
          <p>PDF cannot be displayed.</p>
        </object>
      )}
    </VStack>
  );
};
