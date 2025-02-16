import { VStack, Text } from "@chakra-ui/react";
import React from "react";

interface PDFPreviewProps {
  page: number;
}

export const PDFPreview: React.FC<PDFPreviewProps> = ({ page }) => {
  return (
    <VStack>
      <Text>Displaying page {page} of the PDF.</Text>
    </VStack>
  );
};
