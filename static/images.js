function addImageCell(row, ticket) {
  const cell = document.createElement("td");
  if (ticket.image) {
    const link = document.createElement("a");
    link.href = ticket.image;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", `查看 ${ticket.id} 的問題圖片`);
    const image = document.createElement("img");
    image.src = ticket.image;
    image.alt = `${ticket.id} 的問題圖片`;
    image.className = "ticket-image";
    image.loading = "lazy";
    image.addEventListener("error", () => {
      link.textContent = "圖片無法載入，點此查看";
    });
    link.appendChild(image);
    cell.appendChild(link);
  } else {
    cell.textContent = "未附圖片";
  }
  row.appendChild(cell);
}
