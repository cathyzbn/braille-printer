// ------------------------------------
// pdf-live.tsx
// ------------------------------------
import React, { useEffect, useRef, useState } from "react";
import { VStack, Text, Box } from "@chakra-ui/react";
import { DotPosition, PDFPreviewProps } from "./pdf-preview";
import { fetchApi } from "../../utils/api";

export const PDFLive: React.FC<PDFPreviewProps> = ({ page, dotPositions }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const boxRef = useRef<HTMLDivElement>(null);

  const [currentDotPositions, setCurrentDotPositions] = useState<DotPosition[]>([]);

  useEffect(() => {
    if (!canvasRef.current) {
      return;
    }
    const canvas = canvasRef.current;
    const dpr = 2 * (window.devicePixelRatio || 1);
    
    // Set display size
    const displayWidth = boxRef.current?.clientWidth ?? 0;
    const displayHeight = 11 / 8.5 * displayWidth;
    
    // Set actual pixel size scaled for high DPI displays
    canvas.width = displayWidth * dpr;
    canvas.height = displayHeight * dpr;
    
    // Set display size via CSS
    canvas.style.width = `${displayWidth}px`;
    canvas.style.height = `${displayHeight}px`;
    
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }
    
    // Scale all drawing operations by dpr
    ctx.scale(dpr, dpr);
    
    ctx.clearRect(0, 0, displayWidth, displayHeight);
    // White background
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, displayWidth, displayHeight);
    
    // Black dots
    ctx.imageSmoothingEnabled = true;

    const plotDot = (dot: DotPosition, color: string) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;

      const { x: mmX, y: mmY, punch } = dot;
      const inX = mmX * 0.0393701;
      const inY = mmY * 0.0393701;
      const pxX = inX * displayWidth / 8.5;
      const pxY = inY * displayWidth / 8.5;
      
      if (punch) {
        ctx.fillStyle = color;
      } else {
        ctx.fillStyle = "white";
      }

      ctx.beginPath();
      const radius = 0.0393701 * displayWidth / 8.5;
      ctx.arc(pxX, pxY, radius, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
    }
    
    for (const dot of dotPositions[page]) {
      plotDot(dot, "black");
    }
    for (const dot of currentDotPositions) {
      plotDot(dot, "red");
    }
  }, [page, dotPositions, currentDotPositions, canvasRef, boxRef]);

  useEffect(() => {
    setCurrentDotPositions([]);
    const interval = setInterval(async () => {
      const response = await fetchApi("/printed_dots", {
        method: "POST"
      });
      if (response) {
        const data = await response.json();
        setCurrentDotPositions(data);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [page]);

  return (
    <VStack outlineColor="gray.800" borderRadius="md" width="100%" height="65vh" maxWidth="860px" overflow="hidden">
      <Box width="100%" height="100%" ref={boxRef} overflowY="auto">
      <canvas
        ref={canvasRef}
      >
        <p>PDF cannot be displayed.</p>
      </canvas>
      </Box>
    </VStack>
  );
};
