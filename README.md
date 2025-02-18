# BrailleBot: Turn a 3D Printer to a Braille Printer for $15

> Winner of Treehacks 2025 Best Hardware Hack

**BrailleBot** transforms any document into printed standard braille, well-suited for printing documents, textbooks, websites, or even Zoom lecture summaries. It’s the first printer that can take any document and convert it to an accessible text format including textual image descriptions using AI visual recognition. It then prints the braille using a novel spring-loaded embossing mechanism mounted on a low-cost 3D printer.

Today, the cheapest braille printers are around $1500. Our embossing mechanism costs less than $15, and is then mounted on any low-cost 3D printer. At this price point, our solution is almost 100x cheaper than existing options while maintaining high quality, empowering teachers and students by making learning materials accessible at an unprecedented low price point.


## How we built it

Hardware:
The “punch” mechanism is comprised of a series of 3D printed parts and powered by the printer’s extruder motor, making the modification incredibly fast and inexpensive. A snap action mechanism converts a quarter rotation of the extruder motor into a load and then rapid punch motion. A screw at the top allows the user to adjust the spring’s compression, thereby changing the depth of the punch. The stock extruder can create up to 10 punches a second. 

Software
On the backend, we leverage the Groq inference engine and Zoom API, using Llama3-8B and Llama3-11B Vision to transcribe documents, generate text descriptions of images, and summarize Zoom lecture transcripts with low latency. Then, we use our Python Flask backend to convert the ASCII PDF representations into braille letters and GCode instructions for the Marlin firmware (used by most 3D printers).
Commands are sent to the printer through USB serial.
We use a JS canvas to display a live realtime preview of the print.
The frontend is built with Next.js, Typescript, Chakra, and React.

