import { ApiError, apiRequest } from "./api.js";
import { getCurrentUser, redirectToProjects } from "./auth.js";

const AUTHENTICATION_ERROR_MESSAGE = "ログイン ID またはパスワードが正しくありません。";
const SYSTEM_ERROR_MESSAGE = "予期しないエラーが発生しました。\n時間をおいて再度お試しください。";

const form = document.querySelector("#login-form");
const usernameInput = document.querySelector("#username");
const passwordInput = document.querySelector("#password");
const loginButton = document.querySelector("#login-button");
const loadingMessage = document.querySelector("#login-loading");
const errorMessage = document.querySelector("#login-error");

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}

function setSubmitting(isSubmitting) {
  usernameInput.disabled = isSubmitting;
  passwordInput.disabled = isSubmitting;
  loginButton.disabled = isSubmitting;
  loadingMessage.hidden = !isSubmitting;
}

async function initialize() {
  try {
    await getCurrentUser();
    redirectToProjects();
  } catch (error) {
    if (error instanceof ApiError && error.isUnauthorized) {
      return;
    }
    showError(SYSTEM_ERROR_MESSAGE);
  }
}

async function submitLogin(event) {
  event.preventDefault();
  if (loginButton.disabled) {
    return;
  }

  clearError();
  setSubmitting(true);

  try {
    await apiRequest("/api/auth/login", {
      method: "POST",
      json: {
        username: usernameInput.value,
        password: passwordInput.value,
      },
    });
    redirectToProjects();
  } catch (error) {
    if (error instanceof ApiError && error.isUnauthorized) {
      showError(AUTHENTICATION_ERROR_MESSAGE);
    } else {
      showError(SYSTEM_ERROR_MESSAGE);
    }
    setSubmitting(false);
  }
}

form.addEventListener("submit", submitLogin);
initialize();
