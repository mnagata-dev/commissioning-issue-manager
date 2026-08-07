import { ApiError, apiRequest } from "./api.js";
import {
  clearSelectedProject,
  getCurrentUser,
  handleAuthenticatedApiError,
  logout,
  readSelectedProject,
  redirectToProjects,
} from "./auth.js";

const PAGE_SIZE = 20;
const SEARCH_ERROR_MESSAGE = "検索条件を確認してください。";
const SYSTEM_ERROR_MESSAGE = "予期しないエラーが発生しました。\n時間をおいて再度お試しください。";

const selectedProject = readSelectedProject();
const currentProject = document.querySelector("#current-project");
const currentUser = document.querySelector("#current-user");
const searchForm = document.querySelector("#issue-search-form");
const searchButton = document.querySelector("#search-button");
const loadingMessage = document.querySelector("#issue-loading");
const errorMessage = document.querySelector("#issue-error");
const emptyMessage = document.querySelector("#issue-empty");
const issueList = document.querySelector("#issue-list");
const totalCount = document.querySelector("#total-count");
const currentPage = document.querySelector("#current-page");
const previousButton = document.querySelector("#previous-button");
const nextButton = document.querySelector("#next-button");
const changeProjectButton = document.querySelector("#change-project-button");
const logoutButton = document.querySelector("#logout-button");

let page = 1;
let total = 0;
let activeFilters = {};
let isLoading = false;
let isLoggingOut = false;

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}

function updatePagination() {
  previousButton.disabled = isLoading || page <= 1;
  nextButton.disabled = isLoading || page * PAGE_SIZE >= total;
  currentPage.textContent = String(page);
  totalCount.textContent = String(total);
}

function setLoading(loading) {
  isLoading = loading;
  loadingMessage.hidden = !loading;
  searchButton.disabled = loading;
  updatePagination();
}

function formatUpdatedAt(value) {
  if (typeof value !== "string") {
    return "Updated: Unknown";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Updated: Unknown";
  }
  return `Updated: ${date.toLocaleString()}`;
}

function targetLabel(issue) {
  if (issue.target_type === "ROOM") {
    const roomNumber = issue.room?.room_number;
    return typeof roomNumber === "string" && roomNumber ? `Room ${roomNumber}` : "Room Unknown";
  }
  if (issue.target_type === "OTHER") {
    return typeof issue.target === "string" && issue.target ? `Target: ${issue.target}` : "Target: Unknown";
  }
  return "Target: Unknown";
}

function createIssueItem(issue) {
  const issueData = issue !== null && typeof issue === "object" ? issue : {};
  const article = document.createElement("article");
  article.className = "issue-item";

  const heading = document.createElement("div");
  heading.className = "issue-item-heading";
  const status = document.createElement("span");
  status.className = "status-badge";
  status.textContent = typeof issueData.status === "string" ? issueData.status : "UNKNOWN";
  const category = document.createElement("span");
  category.className = "issue-category";
  category.textContent = typeof issueData.category === "string" ? issueData.category : "Unknown category";
  heading.append(status, category);

  const target = document.createElement("p");
  target.className = "issue-target";
  target.textContent = targetLabel(issueData);
  const description = document.createElement("p");
  description.className = "issue-description";
  description.textContent = typeof issueData.description === "string" ? issueData.description : "Description unavailable.";
  const updatedAt = document.createElement("p");
  updatedAt.className = "issue-updated-at";
  updatedAt.textContent = formatUpdatedAt(issueData.updated_at);

  article.append(heading, target, description, updatedAt);
  if (Number.isInteger(issueData.id)) {
    const link = document.createElement("a");
    link.className = "issue-link";
    const query = new URLSearchParams({ issue_id: String(issueData.id) });
    link.href = `/issue.html?${query.toString()}`;
    link.textContent = "Open Issue";
    article.append(link);
  }
  return article;
}

function renderIssues(items) {
  issueList.replaceChildren();
  for (const issue of items) {
    issueList.append(createIssueItem(issue));
  }
  emptyMessage.hidden = items.length !== 0;
}

function searchFilters() {
  const values = new FormData(searchForm);
  const filters = {};
  for (const name of ["keyword", "status", "category", "target_type"]) {
    const value = values.get(name);
    if (typeof value === "string" && value !== "") {
      filters[name] = value;
    }
  }
  return filters;
}

async function loadIssues(requestedPage) {
  if (isLoading || !selectedProject) {
    return;
  }

  clearError();
  setLoading(true);
  const parameters = new URLSearchParams({
    ...activeFilters,
    page: String(requestedPage),
    page_size: String(PAGE_SIZE),
  });

  try {
    const response = await apiRequest(`/api/projects/${selectedProject.id}/issues?${parameters.toString()}`);
    if (!Array.isArray(response?.items) || !Number.isInteger(response.page) || !Number.isInteger(response.total)) {
      throw new Error("Invalid Issue List response.");
    }
    page = response.page;
    total = response.total;
    renderIssues(response.items);
  } catch (error) {
    if (handleAuthenticatedApiError(error)) {
      return;
    }
    if (error instanceof ApiError && error.status === 404) {
      clearSelectedProject();
      issueList.replaceChildren();
      redirectToProjects();
      return;
    }
    showError(error instanceof ApiError && error.status === 400 ? SEARCH_ERROR_MESSAGE : SYSTEM_ERROR_MESSAGE);
  } finally {
    setLoading(false);
  }
}

async function initialize() {
  if (!selectedProject) {
    redirectToProjects();
    return;
  }

  currentProject.textContent = `Project: ${selectedProject.name} / ${selectedProject.hotel.name}`;
  try {
    const user = await getCurrentUser();
    currentUser.textContent = `${user.display_name} (${user.username})`;
  } catch (error) {
    if (!handleAuthenticatedApiError(error)) {
      showError(SYSTEM_ERROR_MESSAGE);
    }
    return;
  }
  await loadIssues(1);
}

function performSearch(event) {
  event.preventDefault();
  if (isLoading) {
    return;
  }
  activeFilters = searchFilters();
  loadIssues(1);
}

function changePage(offset) {
  const requestedPage = page + offset;
  if (isLoading || requestedPage < 1) {
    return;
  }
  loadIssues(requestedPage);
}

function changeProject() {
  if (isLoading || isLoggingOut) {
    return;
  }
  clearSelectedProject();
  redirectToProjects();
}

async function performLogout() {
  if (isLoading || isLoggingOut) {
    return;
  }
  clearError();
  isLoggingOut = true;
  logoutButton.disabled = true;
  changeProjectButton.disabled = true;
  try {
    await logout();
  } catch {
    showError(SYSTEM_ERROR_MESSAGE);
    isLoggingOut = false;
    logoutButton.disabled = false;
    changeProjectButton.disabled = false;
  }
}

searchForm.addEventListener("submit", performSearch);
previousButton.addEventListener("click", () => changePage(-1));
nextButton.addEventListener("click", () => changePage(1));
changeProjectButton.addEventListener("click", changeProject);
logoutButton.addEventListener("click", performLogout);
initialize();
