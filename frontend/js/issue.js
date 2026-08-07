import { ApiError, apiRequest } from "./api.js";
import {
  getCurrentUser,
  handleAuthenticatedApiError,
  logout,
  readSelectedProject,
  redirectToProjects,
} from "./auth.js";

const SYSTEM_ERROR_MESSAGE = "予期しないエラーが発生しました。\n時間をおいて再度お試しください。";
const EMPTY_COMMENT_MESSAGE = "コメントを入力してください。";
const EMPTY_FILE_MESSAGE = "ファイルを選択してください。";

const currentProject = document.querySelector("#current-project");
const currentUser = document.querySelector("#current-user");
const loadingMessage = document.querySelector("#issue-loading");
const successMessage = document.querySelector("#issue-message");
const errorMessage = document.querySelector("#issue-error");
const issueContent = document.querySelector("#issue-content");
const statusValue = document.querySelector("#issue-status");
const targetTypeValue = document.querySelector("#issue-target-type");
const roomDetail = document.querySelector("#room-detail");
const roomValue = document.querySelector("#issue-room");
const targetDetail = document.querySelector("#target-detail");
const targetValue = document.querySelector("#issue-target");
const categoryValue = document.querySelector("#issue-category");
const descriptionValue = document.querySelector("#issue-description");
const createdByValue = document.querySelector("#issue-created-by");
const createdAtValue = document.querySelector("#issue-created-at");
const updatedByValue = document.querySelector("#issue-updated-by");
const updatedAtValue = document.querySelector("#issue-updated-at");
const commentsEmpty = document.querySelector("#comments-empty");
const commentList = document.querySelector("#comment-list");
const addCommentButton = document.querySelector("#add-comment-button");
const commentForm = document.querySelector("#comment-form");
const commentInput = document.querySelector("#comment-input");
const commentSubmitButton = document.querySelector("#comment-submit-button");
const commentCancelButton = document.querySelector("#comment-cancel-button");
const attachmentsEmpty = document.querySelector("#attachments-empty");
const attachmentList = document.querySelector("#attachment-list");
const uploadAttachmentButton = document.querySelector("#upload-attachment-button");
const attachmentForm = document.querySelector("#attachment-form");
const attachmentInput = document.querySelector("#attachment-input");
const attachmentSubmitButton = document.querySelector("#attachment-submit-button");
const attachmentCancelButton = document.querySelector("#attachment-cancel-button");
const editIssueLink = document.querySelector("#edit-issue-link");
const logoutButton = document.querySelector("#logout-button");

let issueId = null;
let isLoading = false;
let isSubmittingComment = false;
let isUploadingAttachment = false;
let isLoggingOut = false;

function parseIssueId() {
  const value = new URLSearchParams(window.location.search).get("issue_id");
  if (typeof value !== "string" || !/^[1-9]\d*$/.test(value)) {
    return null;
  }
  const parsedValue = Number(value);
  return Number.isSafeInteger(parsedValue) ? parsedValue : null;
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}

function showSuccess(message) {
  successMessage.textContent = message;
  successMessage.hidden = false;
}

function clearSuccess() {
  successMessage.textContent = "";
  successMessage.hidden = true;
}

function redirectToIssues() {
  issueContent.hidden = true;
  window.location.assign("/issues.html");
}

function handleIssueApiError(error) {
  if (handleAuthenticatedApiError(error)) {
    issueContent.hidden = true;
    return true;
  }
  if (error instanceof ApiError && error.status === 404) {
    redirectToIssues();
    return true;
  }
  return false;
}

function textOrFallback(value, fallback = "Unknown") {
  return typeof value === "string" && value ? value : fallback;
}

function formatDateTime(value) {
  if (typeof value !== "string") {
    return "Unknown";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unknown" : date.toLocaleString();
}

function formatFileSize(value) {
  if (!Number.isFinite(value) || value < 0) {
    return "Unknown size";
  }
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KiB`;
  }
  return `${(value / (1024 * 1024)).toFixed(1)} MiB`;
}

function renderTarget(issue) {
  const targetType = textOrFallback(issue.target_type);
  targetTypeValue.textContent = targetType;
  roomDetail.hidden = targetType !== "ROOM";
  targetDetail.hidden = targetType !== "OTHER";
  roomValue.textContent = targetType === "ROOM" ? textOrFallback(issue.room?.room_number) : "";
  targetValue.textContent = targetType === "OTHER" ? textOrFallback(issue.target) : "";
}

function createCommentItem(comment) {
  const item = document.createElement("article");
  item.className = "detail-list-item";
  const author = document.createElement("p");
  author.className = "item-author";
  author.textContent = textOrFallback(comment?.created_by?.display_name);
  const text = document.createElement("p");
  text.className = "item-text";
  text.textContent = textOrFallback(comment?.comment, "Comment unavailable.");
  const timestamp = document.createElement("p");
  timestamp.className = "item-metadata";
  timestamp.textContent = formatDateTime(comment?.created_at);
  item.append(author, text, timestamp);
  return item;
}

function renderComments(comments) {
  commentList.replaceChildren();
  const items = Array.isArray(comments) ? comments : [];
  for (const comment of items) {
    commentList.append(createCommentItem(comment));
  }
  commentsEmpty.hidden = items.length !== 0;
}

function createAttachmentItem(attachment) {
  const item = document.createElement("article");
  item.className = "detail-list-item attachment-item";
  const name = document.createElement("p");
  name.className = "item-author";
  name.textContent = textOrFallback(attachment?.file_name, "File unavailable");
  const metadata = document.createElement("p");
  metadata.className = "item-metadata";
  metadata.textContent = `${textOrFallback(attachment?.mime_type, "Unknown type")} · ${formatFileSize(attachment?.file_size)} · ${formatDateTime(attachment?.uploaded_at)}`;
  item.append(name, metadata);
  if (Number.isSafeInteger(attachment?.id) && attachment.id > 0) {
    const link = document.createElement("a");
    link.href = `/api/attachments/${attachment.id}`;
    link.textContent = "Open Attachment";
    link.target = "_blank";
    link.rel = "noopener";
    item.append(link);
  }
  return item;
}

function renderAttachments(attachments) {
  attachmentList.replaceChildren();
  const items = Array.isArray(attachments) ? attachments : [];
  for (const attachment of items) {
    attachmentList.append(createAttachmentItem(attachment));
  }
  attachmentsEmpty.hidden = items.length !== 0;
}

function renderIssue(issue) {
  currentProject.textContent = `Project: ${textOrFallback(issue.project?.name)}`;
  statusValue.textContent = textOrFallback(issue.status);
  renderTarget(issue);
  categoryValue.textContent = textOrFallback(issue.category);
  descriptionValue.textContent = textOrFallback(issue.description, "Description unavailable.");
  createdByValue.textContent = textOrFallback(issue.created_by?.display_name);
  createdAtValue.textContent = formatDateTime(issue.created_at);
  updatedByValue.textContent = textOrFallback(issue.updated_by?.display_name);
  updatedAtValue.textContent = formatDateTime(issue.updated_at);
  renderComments(issue.comments);
  renderAttachments(issue.attachments);
  const query = new URLSearchParams({ issue_id: String(issueId) });
  editIssueLink.href = `/issue-edit.html?${query.toString()}`;
  issueContent.hidden = false;
}

function setPageActionsDisabled(disabled) {
  addCommentButton.disabled = disabled;
  uploadAttachmentButton.disabled = disabled;
}

async function loadIssue() {
  if (isLoading || issueId === null) {
    return false;
  }
  isLoading = true;
  loadingMessage.hidden = false;
  setPageActionsDisabled(true);
  try {
    const issue = await apiRequest(`/api/issues/${issueId}`);
    if (issue === null || typeof issue !== "object") {
      throw new Error("Invalid Issue Detail response.");
    }
    renderIssue(issue);
    return true;
  } catch (error) {
    if (!handleIssueApiError(error)) {
      showError(SYSTEM_ERROR_MESSAGE);
    }
    return false;
  } finally {
    isLoading = false;
    loadingMessage.hidden = true;
    setPageActionsDisabled(false);
  }
}

function toggleForm(form, input, show) {
  form.hidden = !show;
  if (show) {
    input.focus();
  }
}

async function submitComment(event) {
  event.preventDefault();
  if (isSubmittingComment || issueId === null) {
    return;
  }
  const comment = commentInput.value.trim();
  clearError();
  clearSuccess();
  if (!comment) {
    showError(EMPTY_COMMENT_MESSAGE);
    commentInput.focus();
    return;
  }
  isSubmittingComment = true;
  commentSubmitButton.disabled = true;
  commentCancelButton.disabled = true;
  try {
    await apiRequest(`/api/issues/${issueId}/comments`, { method: "POST", json: { comment } });
    const refreshed = await loadIssue();
    if (refreshed) {
      commentInput.value = "";
      toggleForm(commentForm, commentInput, false);
      showSuccess("Comment を追加しました。");
    }
  } catch (error) {
    if (!handleIssueApiError(error)) {
      showError(error instanceof ApiError && error.status === 400 ? error.message : SYSTEM_ERROR_MESSAGE);
    }
  } finally {
    isSubmittingComment = false;
    commentSubmitButton.disabled = false;
    commentCancelButton.disabled = false;
  }
}

async function uploadAttachment(event) {
  event.preventDefault();
  if (isUploadingAttachment || issueId === null) {
    return;
  }
  const file = attachmentInput.files?.[0];
  clearError();
  clearSuccess();
  if (!file) {
    showError(EMPTY_FILE_MESSAGE);
    attachmentInput.focus();
    return;
  }
  const body = new FormData();
  body.append("file", file);
  isUploadingAttachment = true;
  attachmentSubmitButton.disabled = true;
  attachmentCancelButton.disabled = true;
  try {
    await apiRequest(`/api/issues/${issueId}/attachments`, { method: "POST", body });
    const refreshed = await loadIssue();
    if (refreshed) {
      attachmentForm.reset();
      toggleForm(attachmentForm, attachmentInput, false);
      showSuccess("Attachment をアップロードしました。");
    }
  } catch (error) {
    if (!handleIssueApiError(error)) {
      showError(error instanceof ApiError && error.status === 400 ? error.message : SYSTEM_ERROR_MESSAGE);
    }
  } finally {
    isUploadingAttachment = false;
    attachmentSubmitButton.disabled = false;
    attachmentCancelButton.disabled = false;
  }
}

async function performLogout() {
  if (isLoggingOut) {
    return;
  }
  clearError();
  isLoggingOut = true;
  logoutButton.disabled = true;
  try {
    await logout();
  } catch {
    showError(SYSTEM_ERROR_MESSAGE);
    isLoggingOut = false;
    logoutButton.disabled = false;
  }
}

async function initialize() {
  issueId = parseIssueId();
  if (issueId === null) {
    redirectToIssues();
    return;
  }
  const selectedProject = readSelectedProject();
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
      loadingMessage.hidden = true;
      showError(SYSTEM_ERROR_MESSAGE);
    }
    return;
  }
  await loadIssue();
}

addCommentButton.addEventListener("click", () => toggleForm(commentForm, commentInput, true));
commentCancelButton.addEventListener("click", () => toggleForm(commentForm, commentInput, false));
commentForm.addEventListener("submit", submitComment);
uploadAttachmentButton.addEventListener("click", () => toggleForm(attachmentForm, attachmentInput, true));
attachmentCancelButton.addEventListener("click", () => toggleForm(attachmentForm, attachmentInput, false));
attachmentForm.addEventListener("submit", uploadAttachment);
logoutButton.addEventListener("click", performLogout);
initialize();
