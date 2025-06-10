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

  container.appendChild(win); // must be added to measure size

  // center the window after measuring
  const winWidth = win.offsetWidth || 500;
  const winHeight = win.offsetHeight || 400;
  win.style.left = `${(window.innerWidth - winWidth) / 2}px`;
  win.style.top = `${(window.innerHeight - winHeight) / 2}px`;

  // assign top zindex to new windows
  win.style.zIndex = topZIndex++;

  // event listener for focus (bring to front)
  win.addEventListener("mousedown", () => {
    win.style.zIndex = topZIndex++;
  });

  const titleBar = win.querySelector(".title-bar");
  let offsetX, offsetY, isDragging = false;

  // drag logic
  titleBar.addEventListener("mousedown", (e) => {
    isDragging = true;
    offsetX = e.clientX - win.offsetLeft;
    offsetY = e.clientY - win.offsetTop;
    win.style.zIndex = topZIndex++; // bring window to focus
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

  // close button
  win.querySelector(".close-btn").addEventListener("click", () => {
    win.remove();
  });
}

// digital clock for navbar
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