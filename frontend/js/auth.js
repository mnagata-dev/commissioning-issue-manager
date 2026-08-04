import { ApiError, apiRequest } from "./api.js";

const SELECTED_PROJECT_KEY = "cim.selectedProject";

function isValidProject(project) {
  return (
    project !== null &&
    typeof project === "object" &&
    Number.isInteger(project.id) &&
    typeof project.name === "string" &&
    project.hotel !== null &&
    typeof project.hotel === "object" &&
    Number.isInteger(project.hotel.id) &&
    typeof project.hotel.name === "string"
  );
}

export function getCurrentUser() {
  return apiRequest("/api/auth/me");
}

export function redirectToLogin() {
  window.location.assign("/");
}

export function redirectToProjects() {
  window.location.assign("/projects.html");
}

export function clearSelectedProject() {
  sessionStorage.removeItem(SELECTED_PROJECT_KEY);
}

export function readSelectedProject() {
  const storedValue = sessionStorage.getItem(SELECTED_PROJECT_KEY);
  if (storedValue === null) {
    return null;
  }

  try {
    const project = JSON.parse(storedValue);
    if (isValidProject(project)) {
      return project;
    }
  } catch {
    // Invalid stored data is removed below.
  }

  clearSelectedProject();
  return null;
}

export function storeSelectedProject(project) {
  if (!isValidProject(project)) {
    clearSelectedProject();
    return false;
  }

  const selectedProject = {
    id: project.id,
    name: project.name,
    hotel: {
      id: project.hotel.id,
      name: project.hotel.name,
    },
  };
  sessionStorage.setItem(SELECTED_PROJECT_KEY, JSON.stringify(selectedProject));
  return true;
}

export function handleAuthenticatedApiError(error) {
  if (error instanceof ApiError && error.isUnauthorized) {
    clearSelectedProject();
    redirectToLogin();
    return true;
  }
  return false;
}

export async function logout() {
  try {
    await apiRequest("/api/auth/logout", { method: "POST" });
  } catch (error) {
    if (error instanceof ApiError && error.isUnauthorized) {
      clearSelectedProject();
      redirectToLogin();
      return;
    }
    throw error;
  }

  clearSelectedProject();
  redirectToLogin();
}
