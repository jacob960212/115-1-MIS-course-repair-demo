const form = document.querySelector("#ticket-form");
const message = document.querySelector("#message");
const table = document.querySelector("#ticket-table");
const tableBody = table.querySelector("tbody");
const emptyState = document.querySelector("#empty-state");
const refreshButton = document.querySelector("#refresh-button");
const imageInput = document.querySelector("#image-input");
const submitButton = form.querySelector('button[type="submit"]');

function validateImage() {
  const file = imageInput.files[0];
  let error = "";
  if (file && !/\.(jpe?g|png|gif|webp)$/i.test(file.name)) {
    error = "圖片格式不支援，請選擇 JPG、PNG、GIF 或 WebP。";
  } else if (file && file.size > 5 * 1024 * 1024) {
    error = "圖片不得超過 5 MB，請縮小圖片後再送出。";
  }
  imageInput.setCustomValidity(error);
  return error;
}

imageInput.addEventListener("change", () => {
  showMessage(validateImage(), !!imageInput.validationMessage);
});

function showMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle("error", isError);
}

function addCell(row, value) {
  const cell = document.createElement("td");
  cell.textContent = value;
  row.appendChild(cell);
}

function renderTickets(tickets) {
  tableBody.replaceChildren();
  emptyState.hidden = tickets.length > 0;
  table.hidden = tickets.length === 0;

  for (const ticket of tickets) {
    const row = document.createElement("tr");
    addCell(row, ticket.id);
    addCell(row, ticket.location);
    addCell(row, ticket.equipment);
    addCell(row, ticket.urgency);
    addCell(row, ticket.contact);
    addCell(row, ticket.status);
    addCell(row, ticket.description);
    addImageCell(row, ticket);
    addCell(row, ticket.created_at);
    tableBody.appendChild(row);
  }
}

async function loadTickets() {
  try {
    const response = await fetch("/api/tickets");
    if (!response.ok) throw new Error("無法讀取案件清單");
    renderTickets(await response.json());
  } catch (error) {
    showMessage(error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const imageError = validateImage();
  if (imageError) {
    showMessage(imageError, true);
    return;
  }
  showMessage("正在建立報修單…");
  submitButton.disabled = true;

  const formData = new FormData(form);

  try {
    const response = await fetch("/api/tickets", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();

    if (!response.ok) throw new Error(result.message || "建立報修單失敗");

    showMessage(result.message);
    form.reset();
    imageInput.setCustomValidity("");
    await loadTickets();
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

refreshButton.addEventListener("click", loadTickets);
loadTickets();
