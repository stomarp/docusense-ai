import {
  AnalysisResponseSchema,
  UploadResponseSchema,
  type AnalysisResponse,
  type UploadResponse
} from "./schemas";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8010";

async function parseJsonResponse<T>(
  response: Response,
  parser: { parse: (value: unknown) => T },
  errorMessage: string
): Promise<T> {
  if (!response.ok) {
    throw new Error(errorMessage);
  }

  const payload = await response.json();

  try {
    return parser.parse(payload);
  } catch {
    throw new Error("API response shape did not match the DocuSense frontend contract.");
  }
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(API_BASE_URL + "/upload", {
    method: "POST",
    body: formData
  });

  return parseJsonResponse(response, UploadResponseSchema, "Upload failed");
}

export async function analyzeDocument(storedFilename: string): Promise<AnalysisResponse> {
  const response = await fetch(API_BASE_URL + "/analyze/" + storedFilename, {
    method: "POST"
  });

  return parseJsonResponse(response, AnalysisResponseSchema, "Analysis failed");
}

export type { AnalysisResponse, UploadResponse };
