import useSWR from 'swr';

// Define a type for the principle data, if known, otherwise use 'any' for now.
// For example:
// interface Principle {
//   id: string;
//   title: string;
//   content: string;
//   // other fields
// }

const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) {
    const error = new Error('An error occurred while fetching the data.');
    // Attach extra info to the error object.
    // try {
    //   error.info = await res.json();
    // } catch (e) {
    //   // If API doesn't return JSON or it's unparseable
    //   error.info = { message: await res.text() };
    // }
    // error.status = res.status;
    throw error;
  }
  try {
    return await res.json();
  } catch (e) {
    const error = new Error('Failed to parse JSON response.');
    // error.info = { message: await res.text() }; // Or some other way to capture raw response
    // error.status = res.status; // Keep original status if needed
    throw error;
  }
};

export function usePrinciple(principleId: string | null) {
  // Replace 'any' with the actual Principle type if available
  const { data, error, isLoading } = useSWR<any>(
    principleId ? `/api/principles/${principleId}` : null,
    fetcher
  );

  return {
    principle: data,
    isLoading,
    isError: error,
  };
}
