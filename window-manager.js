let topZIndex = 100; // track zindex

function createCoplandWindow(title, url) {
  const container = document.getElementById("window-container");

  const win = document.createElement("div");
  win.className = "copland-window";
  win.innerHTML = `
    <div class="title-bar">
      <div class="window-title">${title}</div>
      <button class="close-btn">X</button>
    </div>
    <iframe src="${url}" frameborder="0" style="background: transparent;"></iframe>
  `;

  // assign top zindex to new windows
  win.style.zIndex = topZIndex++;

  // event listener for focus
  win.addEventListener("mousedown", () => {
    win.style.zIndex = topZIndex++;
    win.style.left = `${(window.innerWidth - 500) / 2}px`;
    win.style.top = `${(window.innerHeight - 400) / 2}px`;
  });

  container.appendChild(win);

  const titleBar = win.querySelector(".title-bar");
  let offsetX, offsetY, isDragging = false;

  
  titleBar.addEventListener("mousedown", (e) => {
    isDragging = true;
    offsetX = e.clientX - win.offsetLeft;
    offsetY = e.clientY - win.offsetTop;
    win.style.zIndex = topZIndex++; // bring window to focus, needs better implementation
  });

  document.addEventListener("mousemove", (e) => {
    if (isDragging) {
      win.style.left = `${e.clientX - offsetX}px`;
      win.style.top = `${e.clientY - offsetY}px`;
    }
  });

  document.addEventListener("mouseup", () => {
    isDragging = false;
  });

  
  win.querySelector(".close-btn").addEventListener("click", () => {
    win.remove();
  });
}

function updateClock() {
  const clock = document.getElementById("clock");
  const now = new Date();

  let hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, "0");
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;

  const month = (now.getMonth() + 1).toString().padStart(2, "0");
  const day = now.getDate().toString().padStart(2, "0");
  const year = now.getFullYear().toString().slice(-2);

  const formatted = ` ${hours}:${minutes} ${ampm} ${month}/${day}/${year}`;
  clock.textContent = formatted;
}

setInterval(updateClock, 1000);
updateClock();