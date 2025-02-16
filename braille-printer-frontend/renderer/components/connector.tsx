import { Button, createListCollection, SelectContent, SelectItem, SelectLabel, SelectRoot, SelectTrigger, SelectValueText, Stack } from "@chakra-ui/react";
import { useState } from "react";
import { fetchApi } from "../utils/api";

const ports = createListCollection({
  items: [
    { label: "usbserial-0001", value: "/dev/tty.usbserial-0001" },
  ]
});

const baudRates = createListCollection({
  items: [
    { label: "9600", value: "9600" },
    { label: "14400", value: "14400" },
    { label: "19200", value: "19200" },
    { label: "28800", value: "28800" },
    { label: "38400", value: "38400" },
    { label: "56000", value: "56000" }, 
    { label: "57600", value: "57600" },
    { label: "76800", value: "76800" },
    { label: "111112", value: "111112" },
    { label: "115200", value: "115200" },
    { label: "128000", value: "128000" },
    { label: "230400", value: "230400" },
    { label: "250000", value: "250000" },
    { label: "256000", value: "256000" },
    { label: "460800", value: "460800" },
    { label: "500000", value: "500000" },
    { label: "921600", value: "921600" },
    { label: "1000000", value: "1000000" },
    { label: "1382400", value: "1382400" },
    { label: "1500000", value: "1500000" },
    { label: "2000000", value: "2000000" },
  ]
});

interface ConnectorProps {  
  isConnected: boolean;
  setIsConnected: (isConnected: boolean) => void;
}

export const Connector = ({ isConnected, setIsConnected }: ConnectorProps) => {
  const [port, setPort] = useState<string[]>(["/dev/tty.usbserial-0001"]);
  const [baudRate, setBaudRate] = useState<string[]>(["250000"]);
  const [loading, setLoading] = useState<boolean>(false);

  const disconnect = async () => {
    setLoading(true);
    const response = await fetchApi("/disconnect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (response) {
      setIsConnected(false);
    }
    setLoading(false);
  };

  const connect = async () => {
    setLoading(true);
    const response = await fetchApi("/connect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        port: port[0],
        baudRate: parseInt(baudRate[0]),
      }),
    });
    if (response) {
      setIsConnected(true);
    }
    setLoading(false);
  };

  if (isConnected) {
    return <Button onClick={disconnect} loading={loading} variant="outline" marginRight={0}>Disconnect</Button>;
  }
  
  return (
    <Stack>
      <SelectRoot collection={ports} size="sm" width="320px" value={port} onValueChange={(e) => setPort(e.value)}>
        <SelectLabel>Select port</SelectLabel>
        <SelectTrigger>
          <SelectValueText placeholder="Select port" />
        </SelectTrigger>
        <SelectContent>
          {ports.items.map((port) => (
            <SelectItem item={port} key={port.value}>
              {port.label}
            </SelectItem>
          ))}
        </SelectContent>
      </SelectRoot>
      <SelectRoot collection={baudRates} size="sm" width="320px" value={baudRate} onValueChange={(e) => setBaudRate(e.value)}>
        <SelectLabel>Select baud rate</SelectLabel>
        <SelectTrigger> 
          <SelectValueText placeholder="Select baud rate" />
        </SelectTrigger>
        <SelectContent>
          {baudRates.items.map((baudRate) => (
            <SelectItem item={baudRate} key={baudRate.value}>
              {baudRate.label}
            </SelectItem>
          ))}
        </SelectContent>
      </SelectRoot>
      <Button onClick={connect} disabled={port.length === 0 || baudRate.length === 0} loading={loading}>Connect</Button>
    </Stack>
  );
};
