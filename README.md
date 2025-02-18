# BrailleBot: Turn a 3D Printer to a Braille Printer for $15

**BrailleBot** transforms any document into printed standard braille, well-suited for printing documents, textbooks, websites, or even Zoom lecture summaries. It’s the first printer that can take any document and convert it to an accessible text format including textual image descriptions using AI visual recognition. It then prints the braille using a novel spring-loaded embossing mechanism mounted on a low-cost 3D printer.

Today, the cheapest braille printers are around $1500. Our embossing mechanism costs less than $15, and is then mounted on any low-cost 3D printer. At this price point, our solution is almost 100x cheaper than existing options while maintaining high quality, empowering teachers and students by making learning materials accessible at an unprecedented low price point.

## Why build this?

During the start of Treehacks, we chatted with a fellow builder who described corresponding with her visually-impaired pen pal: She types her message on her computer, and then manually punches the braille, letter by letter, on a sheet of paper to send over.

Why does she do this? Braille printers are outrageously expensive due to the high degree of precision required and the niche market. Due to the high cost, many who seek to print braille documents instead manually punch each letter with a specialized hole puncher.

This struggle extends far beyond personal correspondence—it highlights a critical gap in education for the visually impaired. A low-cost Braille printer could empower teachers and students, making learning materials accessible to those in low-income communities, individuals who are both visually and audibly impaired, and those who rely on long-lasting, tangible print to acquire knowledge and information.

That's when we had our breakthrough. Modern 3D printers offer incredible precision at a fraction of the cost of specialized equipment. By retrofitting a basic 3D printer with our custom embossing mechanism, we created a braille printer that maintains professional-grade accuracy while cutting costs by nearly 99%.
We didn't stop at making braille printing affordable. Today, only 3% of the internet is accessible to visually impaired users, largely because most content creators don't include text descriptions for images and visuals. We realized that we can use AI to describe images and convert any document to an accessible format. 

We believe that document format or visual content should never be a barrier to access, and with BrailleBot, sharing ideas can be as simple as pressing 'print' for everyone.

## How we built it

Hardware:
The “punch” mechanism is comprised of a series of 3D printed parts and powered by the printer’s extruder motor, making the modification incredibly fast and inexpensive. A snap action mechanism converts a quarter rotation of the extruder motor into a load and then rapid punch motion. A screw at the top allows the user to adjust the spring’s compression, thereby changing the depth of the punch. The stock extruder can create up to 10 punches a second. 

Software
On the backend, we leverage the Groq inference engine and Zoom API, using Llama3-8B and Llama3-11B Vision to transcribe documents, generate text descriptions of images, and summarize Zoom lecture transcripts with low latency. Then, we use our Python Flask backend to convert the ASCII PDF representations into braille letters and GCode instructions for the Marlin firmware (used by most 3D printers).
Commands are sent to the printer through USB serial.
We use a JS canvas to display a live realtime preview of the print.
The frontend is built with Next.js, Typescript, Chakra, and React.

## Challenges we ran into

Finding the right combination of punch geometry, travel distance, and impact material was a challenge on both the software and hardware side because of the limited resources on hand and criteria that the product be cheap and easy to retrofit. We tried a variety of foams, cloths, and papers, eventually landing on a cork sheet which can be purchased at hobby stores for a few dollars. This had the right amount of compliance to make a clear mark without punching through the paper. We also created a mechanism to iteratively test spring compressions and travel distances by having an adjustable spring and head offset, allowing us to efficiently explore a large design space. We 3D-printed multiple punch heads to ensure the best tactile experience.

## Reflection

It was so fun to build the braille printer together, combining each of our unique focus areas. Scott is an EE, Lawton is a MechE, Cathy specializes in AI, and Jason in front-end, resulting in a full-stack team. Building parts of the project and handing them off to each other felt like handing off the baton in a relay race. We’re proud that the resultant product works with a high degree of accuracy, and we were surprised at how low we were able to make the total cost of materials. On the software front, we're proud to be able to make all document formats accessible, from PDFs and word documents to scanned images using OCR.
Above all, we're most proud of creating something that could make a real difference in people's lives. Building an affordable, reliable braille printer that can handle multiple document types means more visually impaired people can have access to printed materials in their preferred format.

## What's next for BrailleBot: Make Every Document Accessible!

We plan to open-source our work, so anyone seeking to build a braille printer can do so at low cost. We will include detailed documentation, files, and backend code logic, 3D printed prototypes, such that anyone can replicate our build.
