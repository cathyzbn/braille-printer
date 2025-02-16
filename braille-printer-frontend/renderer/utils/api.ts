
import { toaster } from "../components/ui/toaster";

export async function fetchApi(path: string, options: RequestInit, { errorTitle = "Error" }: { errorTitle?: string } = { errorTitle: "Error" }) {
  try {
    const response = await fetch(`http://localhost:6969${path}`, options);
    if (response.ok) {
      return response;
    } else {
      try {
        const data = await response.json();
        if (data.error) { 
          toaster.error({
            title: errorTitle,
            description: data.error,
          });
        }
      } catch {
        toaster.error({
          title: errorTitle,
          description: response.statusText,
        });
        return null;
      }
    }
  } catch (error) {
    if (error instanceof Error) {
      toaster.error({
        title: errorTitle,
        description: error.message,
      });
    } else {
      toaster.error({
        title: errorTitle,
        description: String(error),
      });
    }
    return null;
  }
};
