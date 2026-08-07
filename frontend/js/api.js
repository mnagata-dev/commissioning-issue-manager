export class ApiError extends Error {
  constructor(status, code, message) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }

  get isUnauthorized() {
    return this.status === 401;
  }
}

function isJsonResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  return contentType.toLowerCase().includes("application/json");
}

async function parseJson(response) {
  if (response.status === 204) {
    return null;
  }

  const body = await response.text();
  if (!body) {
    return null;
  }

  if (!isJsonResponse(response)) {
    throw new ApiError(response.status, "INVALID_RESPONSE", "Unexpected response type.");
  }

  try {
    return JSON.parse(body);
  } catch {
    throw new ApiError(response.status, "INVALID_RESPONSE", "Invalid JSON response.");
  }
}

function errorDetails(data) {
  if (
    data &&
    typeof data === "object" &&
    data.error &&
    typeof data.error === "object"
  ) {
    return {
      code: typeof data.error.code === "string" ? data.error.code : "API_ERROR",
      message:
        typeof data.error.message === "string"
          ? data.error.message
          : "The API request failed.",
    };
  }

  return { code: "API_ERROR", message: "The API request failed." };
}

export async function apiRequest(path, options = {}) {
  const requestOptions = {
    method: options.method || "GET",
    credentials: "same-origin",
  };

  if (Object.hasOwn(options, "json")) {
    requestOptions.headers = { "Content-Type": "application/json" };
    requestOptions.body = JSON.stringify(options.json);
  } else if (Object.hasOwn(options, "body")) {
    requestOptions.body = options.body;
  }

  const response = await fetch(path, requestOptions);
  const data = await parseJson(response);

  if (!response.ok) {
    const details = errorDetails(data);
    throw new ApiError(response.status, details.code, details.message);
  }

  return data;
}
