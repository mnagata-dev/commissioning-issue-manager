import { apiRequest } from "./api.js";
import {
  clearSelectedProject,
  getCurrentUser,
  handleAuthenticatedApiError,
  logout,
  readSelectedProject,
  storeSelectedProject,
} from "./auth.js";

const SYSTEM_ERROR_MESSAGE = "予期しないエラーが発生しました。\n時間をおいて再度お試しください。";
const SELECTION_ERROR_MESSAGE = "Project を選択してください。";

const currentUser = document.querySelector("#current-user");
const projectForm = document.querySelector("#project-form");
const projectFieldset = document.querySelector("#project-fieldset");
const projectList = document.querySelector("#project-list");
const loadingMessage = document.querySelector("#project-loading");
const emptyMessage = document.querySelector("#project-empty");
const errorMessage = document.querySelector("#project-error");
const selectButton = document.querySelector("#select-project-button");
const logoutButton = document.querySelector("#logout-button");

let projects = [];
let isSelecting = false;
let isLoggingOut = false;

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

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}

function selectedProjectId() {
  const selectedControl = projectForm.elements.namedItem("project");
  if (!selectedControl) {
    return null;
  }

  if (selectedControl instanceof RadioNodeList) {
    return selectedControl.value ? Number(selectedControl.value) : null;
  }
  return selectedControl.checked ? Number(selectedControl.value) : null;
}

function updateSelectButton() {
  selectButton.disabled = isSelecting || selectedProjectId() === null;
}

function createProjectItem(project, checked) {
  const label = document.createElement("label");
  label.className = "project-item";

  const radio = document.createElement("input");
  radio.type = "radio";
  radio.name = "project";
  radio.value = String(project.id);
  radio.checked = checked;
  radio.addEventListener("change", () => {
    clearError();
    updateSelectButton();
  });

  const description = document.createElement("span");
  const projectName = document.createElement("span");
  projectName.className = "project-name";
  projectName.textContent = project.name;
  const hotelName = document.createElement("span");
  hotelName.className = "hotel-name";
  hotelName.textContent = project.hotel.name;

  description.append(projectName, hotelName);
  label.append(radio, description);
  return label;
}

function renderProjects() {
  const storedProject = readSelectedProject();
  const storedProjectExists = storedProject
    ? projects.some((project) => project.id === storedProject.id)
    : false;

  if (storedProject && !storedProjectExists) {
    clearSelectedProject();
  }

  projectList.replaceChildren();
  for (const project of projects) {
    projectList.append(createProjectItem(project, storedProjectExists && project.id === storedProject.id));
  }

  emptyMessage.hidden = projects.length !== 0;
  projectFieldset.disabled = projects.length === 0;
  updateSelectButton();
}

async function initialize() {
  try {
    const user = await getCurrentUser();
    currentUser.textContent = `${user.display_name} (${user.username})`;

    const response = await apiRequest("/api/projects");
    if (!Array.isArray(response?.projects) || !response.projects.every(isValidProject)) {
      throw new Error("Invalid Project response.");
    }
    projects = response.projects;
    renderProjects();
  } catch (error) {
    if (!handleAuthenticatedApiError(error)) {
      showError(SYSTEM_ERROR_MESSAGE);
    }
  } finally {
    loadingMessage.hidden = true;
  }
}

function selectProject(event) {
  event.preventDefault();
  if (isSelecting) {
    return;
  }

  clearError();
  const projectId = selectedProjectId();
  const project = projects.find((item) => item.id === projectId);
  if (!project) {
    showError(SELECTION_ERROR_MESSAGE);
    updateSelectButton();
    return;
  }

  isSelecting = true;
  projectFieldset.disabled = true;
  selectButton.disabled = true;
  selectButton.textContent = "移動中です…";

  if (!storeSelectedProject(project)) {
    isSelecting = false;
    projectFieldset.disabled = false;
    selectButton.textContent = "Select Project";
    showError(SYSTEM_ERROR_MESSAGE);
    updateSelectButton();
    return;
  }

  window.location.assign("/issues.html");
}

async function performLogout() {
  if (isLoggingOut || isSelecting) {
    return;
  }

  clearError();
  isLoggingOut = true;
  logoutButton.disabled = true;
  logoutButton.textContent = "ログアウト中です…";
  projectFieldset.disabled = true;
  selectButton.disabled = true;

  try {
    await logout();
  } catch {
    showError(SYSTEM_ERROR_MESSAGE);
    isLoggingOut = false;
    logoutButton.disabled = false;
    logoutButton.textContent = "Logout";
    projectFieldset.disabled = projects.length === 0;
    updateSelectButton();
  }
}

projectForm.addEventListener("submit", selectProject);
logoutButton.addEventListener("click", performLogout);
initialize();
