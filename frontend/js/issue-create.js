import { ApiError, apiRequest } from "./api.js";
import {
  clearSelectedProject,
  getCurrentUser,
  handleAuthenticatedApiError,
  logout,
  readSelectedProject,
  redirectToProjects,
} from "./auth.js";

const SYSTEM_ERROR_MESSAGE = "予期しないエラーが発生しました。\n時間をおいて再度お試しください。";
const AI_ERROR_MESSAGE = "AI Draft の生成に失敗しました。\n入力内容を確認して再度実行してください。";
const selectedProject = readSelectedProject();
const form = document.querySelector("#issue-create-form");
const fields = document.querySelector("#create-fields");
const targetType = document.querySelector("#target-type");
const room = document.querySelector("#room");
const target = document.querySelector("#target");
const category = document.querySelector("#category");
const description = document.querySelector("#description");
const inputText = document.querySelector("#input-text");
const loadingMessage = document.querySelector("#issue-loading");
const errorMessage = document.querySelector("#issue-error");
const draftMessage = document.querySelector("#draft-message");
const logoutButton = document.querySelector("#logout-button");
const cancelLink = document.querySelector("#cancel-link");
let ready = false;
let busy = false;

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearErrors() {
  errorMessage.hidden = true;
  for (const input of [targetType, room, target, category, description, inputText]) {
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

function validateInputs(forDraft) {
  clearErrors();
  const requiredInputs = [
    [targetType, "Target Type を選択してください。"],
    ...(targetType.value === "ROOM" ? [[room, "Room を選択してください。"]] : []),
    ...(targetType.value === "OTHER" ? [[target, "Target を入力してください。"]] : []),
    ...(forDraft
      ? [[inputText, "AI Draft の入力内容を入力してください。"]]
      : [[category, "Category を選択してください。"], [description, "Description を入力してください。"]]),
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

function handleRequestError(error, forDraft = false) {
  if (handleAuthenticatedApiError(error)) {
    ready = false;
    return;
  }
  if (error instanceof ApiError && error.status === 404) {
    ready = false;
    clearSelectedProject();
    redirectToProjects();
    return;
  }
  if (error instanceof ApiError && [400, 409].includes(error.status)) {
    showError("入力内容を確認してください。Room・Target・Category・Description が正しく指定されているか確認してください。");
  } else {
    showError(forDraft && error instanceof ApiError && error.code === "AI_SERVICE_ERROR" ? AI_ERROR_MESSAGE : SYSTEM_ERROR_MESSAGE);
  }
}

async function generateDraft() {
  if (!ready || busy || !validateInputs(true)) {
    return;
  }
  draftMessage.hidden = true;
  setBusy(true, "AI Draft を生成しています…");
  try {
    const response = await apiRequest("/api/ai/issue-draft", {
      method: "POST",
      json: { project_id: selectedProject.id, ...targetRequest(), input_text: inputText.value.trim() },
    });
    if (!response || typeof response.description !== "string" || !response.description.trim() ||
        !Array.from(category.options).some((option) => option.value && option.value === response.category)) {
      throw new Error("Invalid AI Draft response.");
    }
    category.value = response.category;
    description.value = response.description;
    draftMessage.hidden = false;
  } catch (error) {
    handleRequestError(error, true);
  } finally {
    setBusy(false);
  }
}

async function createIssue(event) {
  event.preventDefault();
  if (!ready || busy || !validateInputs(false)) {
    return;
  }
  const request = { ...targetRequest(), category: category.value, description: description.value.trim() };
  setBusy(true, "Issue を登録しています…");
  try {
    const response = await apiRequest(`/api/projects/${selectedProject.id}/issues`, { method: "POST", json: request });
    if (!Number.isSafeInteger(response?.id) || response.id <= 0) {
      throw new Error("Invalid Issue Create response.");
    }
    ready = false;
    window.location.assign(`/issue.html?issue_id=${response.id}`);
  } catch (error) {
    handleRequestError(error);
  } finally {
    setBusy(false);
  }
}

async function initialize() {
  if (!selectedProject) {
    redirectToProjects();
    return;
  }
  document.querySelector("#current-project").textContent = `Project: ${selectedProject.name} / ${selectedProject.hotel.name}`;
  setBusy(true, "読み込んでいます…");
  try {
    const user = await getCurrentUser();
    document.querySelector("#current-user").textContent = `${user.display_name} (${user.username})`;
    const response = await apiRequest(`/api/hotels/${selectedProject.hotel.id}/rooms`);
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
form.addEventListener("submit", createIssue);
document.querySelector("#generate-draft-button").addEventListener("click", generateDraft);
logoutButton.addEventListener("click", performLogout);
cancelLink.addEventListener("click", (event) => {
  if (busy) {
    event.preventDefault();
  }
});
initialize();
