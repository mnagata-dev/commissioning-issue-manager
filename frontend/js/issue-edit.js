import { ApiError, apiRequest } from "./api.js";
import {
  getCurrentUser,
  handleAuthenticatedApiError,
  logout,
  readSelectedProject,
  redirectToProjects,
} from "./auth.js";

const SYSTEM_ERROR_MESSAGE = "予期しないエラーが発生しました。\n時間をおいて再度お試しください。";
const selectedProject = readSelectedProject();
const form = document.querySelector("#issue-edit-form");
const fields = document.querySelector("#edit-fields");
const targetType = document.querySelector("#target-type");
const room = document.querySelector("#room");
const target = document.querySelector("#target");
const category = document.querySelector("#category");
const description = document.querySelector("#description");
const status = document.querySelector("#status");
const issueId = parseIssueId();
const loadingMessage = document.querySelector("#issue-loading");
const errorMessage = document.querySelector("#issue-error");
const logoutButton = document.querySelector("#logout-button");
const cancelLink = document.querySelector("#cancel-link");
let savedStatus = null;
let ready = false;
let busy = false;

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearErrors() {
  errorMessage.hidden = true;
  for (const input of [status, targetType, room, target, category, description]) {
    document.querySelector(`#${input.id}-error`).hidden = true;
    input.removeAttribute("aria-invalid");
  }
}

function setBusy(value, message = "処理中です…") {
  busy = value;
  fields.disabled = busy || !ready;
  logoutButton.disabled = busy;
  loadingMessage.textContent = message;
  loadingMessage.hidden = !busy;
  cancelLink.setAttribute("aria-disabled", String(busy));
}

function updateTargetFields() {
  const isRoom = targetType.value === "ROOM";
  const isOther = targetType.value === "OTHER";
  document.querySelector("#room-field").hidden = !isRoom;
  document.querySelector("#target-field").hidden = !isOther;
  room.disabled = !isRoom;
  room.required = isRoom;
  target.disabled = !isOther;
  target.required = isOther;
}

function validateInputs() {
  clearErrors();
  const requiredInputs = [
    [targetType, "Target Type を選択してください。"],
    ...(targetType.value === "ROOM" ? [[room, "Room を選択してください。"]] : []),
    ...(targetType.value === "OTHER" ? [[target, "Target を入力してください。"]] : []),
    [category, "Category を選択してください。"],
    [description, "Description を入力してください。"],
    [status, "Status を選択してください。"],
  ];
  let firstInvalid = null;
  for (const [input, message] of requiredInputs) {
    if (!input.value.trim()) {
      const error = document.querySelector(`#${input.id}-error`);
      error.textContent = message;
      error.hidden = false;
      input.setAttribute("aria-invalid", "true");
      firstInvalid ??= input;
    }
  }
  firstInvalid?.focus();
  return firstInvalid === null;
}

function targetRequest() {
  return {
    target_type: targetType.value,
    room_id: targetType.value === "ROOM" ? Number(room.value) : null,
    target: targetType.value === "OTHER" ? target.value.trim() : null,
  };
}

function parseIssueId() {
  const value = new URLSearchParams(window.location.search).get("issue_id");
  if (typeof value !== "string" || !/^[1-9]\d*$/.test(value)) {
    return null;
  }
  const parsedValue = Number(value);
  return Number.isSafeInteger(parsedValue) ? parsedValue : null;
}

function handleRequestError(error, contentSaved = false) {
  if (handleAuthenticatedApiError(error)) {
    ready = false;
    return;
  }
  if (error instanceof ApiError && error.status === 404) {
    ready = false;
    window.location.assign("/issues.html");
    return;
  }
  if (contentSaved) {
    showError("Issue の内容は保存済みですが、Status の更新を確認できませんでした。入力内容を確認して再度 Save してください。");
  } else if (error instanceof ApiError && [400, 409].includes(error.status)) {
    showError("入力内容を確認してください。Room・Target・Category・Description が正しく指定されているか確認してください。");
  } else {
    showError(SYSTEM_ERROR_MESSAGE);
  }
}

async function saveIssue(event) {
  event.preventDefault();
  if (!ready || busy || !validateInputs()) {
    return;
  }
  const request = { ...targetRequest(), category: category.value, description: description.value.trim() };
  const requestedStatus = status.value;
  let contentSaved = false;
  setBusy(true, "Issue を保存しています…");
  try {
    await apiRequest(`/api/issues/${issueId}`, { method: "PUT", json: request });
    contentSaved = true;
    if (requestedStatus !== savedStatus) {
      await apiRequest(`/api/issues/${issueId}/status`, { method: "PATCH", json: { status: requestedStatus } });
      savedStatus = requestedStatus;
    }
    ready = false;
    window.location.assign(`/issue.html?issue_id=${issueId}`);
  } catch (error) {
    handleRequestError(error, contentSaved);
  } finally {
    setBusy(false);
  }
}

async function initialize() {
  if (issueId === null) {
    window.location.assign("/issues.html");
    return;
  }
  cancelLink.href = `/issue.html?issue_id=${issueId}`;
  if (!selectedProject) {
    redirectToProjects();
    return;
  }
  document.querySelector("#current-project").textContent = `Project: ${selectedProject.name} / ${selectedProject.hotel.name}`;
  setBusy(true, "読み込んでいます…");
  try {
    const user = await getCurrentUser();
    document.querySelector("#current-user").textContent = `${user.display_name} (${user.username})`;
    const issue = await apiRequest(`/api/issues/${issueId}`);
    // Resolve the Issue's hotel when a direct link differs from the selected Project.
    let project = selectedProject;
    if (issue.project.id !== selectedProject.id) {
      const projects = await apiRequest("/api/projects");
      project = projects.projects.find((item) => item.id === issue.project.id);
      if (!project) {
        throw new Error("Issue Project unavailable.");
      }
    }
    document.querySelector("#current-project").textContent = `Project: ${issue.project.name} / ${project.hotel.name}`;
    const response = await apiRequest(`/api/hotels/${project.hotel.id}/rooms`);
    if (!Array.isArray(response?.rooms)) {
      throw new Error("Invalid Room List response.");
    }
    for (const item of response.rooms) {
      const option = document.createElement("option");
      option.value = String(item.id);
      option.textContent = item.room_number;
      room.append(option);
    }
    document.querySelector("#room-empty").hidden = response.rooms.length !== 0;
    status.value = issue.status;
    savedStatus = issue.status;
    targetType.value = issue.target_type;
    room.value = issue.room ? String(issue.room.id) : "";
    target.value = issue.target ?? "";
    category.value = issue.category;
    description.value = issue.description;
    updateTargetFields();
    ready = true;
  } catch (error) {
    handleRequestError(error);
  } finally {
    setBusy(false);
  }
}

async function performLogout() {
  if (busy) {
    return;
  }
  clearErrors();
  setBusy(true);
  try {
    await logout();
    ready = false;
  } catch {
    showError(SYSTEM_ERROR_MESSAGE);
  } finally {
    setBusy(false);
  }
}

targetType.addEventListener("change", () => {
  clearErrors();
  updateTargetFields();
});
form.addEventListener("submit", saveIssue);
logoutButton.addEventListener("click", performLogout);
cancelLink.addEventListener("click", (event) => {
  if (busy) {
    event.preventDefault();
  }
});
initialize();
