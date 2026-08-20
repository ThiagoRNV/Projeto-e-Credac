document.addEventListener("DOMContentLoaded", () => {
  const arquivoInput = document.getElementById("arquivo_custo");
  const arquivoZone = document.getElementById("arquivoZone");
  const arquivoInfo = document.getElementById("arquivo_custoInfo");
  const processBtnContainer = document.getElementById("processBtnContainer");
  const processBtn = document.getElementById("processBtn");
  const spinner = document.getElementById("spinner");
  const btnText = document.getElementById("btnText");
  const form = document.getElementById("formArquivos");

  if (!arquivoInput || !arquivoZone || !arquivoInfo || !processBtnContainer) {
    return;
  }

  const show = el => el.classList.remove("d-none");
  const hide = el => el.classList.add("d-none");

  function formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  }

  function updateInfo() {
    if (arquivoInput.files.length > 0) {
      const file = arquivoInput.files[0];
      show(arquivoInfo);
      arquivoInfo.innerHTML = `📊 ${file.name} <span class="d-block mt-1 small text-secondary">${formatBytes(file.size)}</span>`;
      show(processBtnContainer);
    } else {
      hide(arquivoInfo);
      hide(processBtnContainer);
    }
  }

  arquivoZone.addEventListener("click", () => arquivoInput.click());

  arquivoZone.addEventListener("dragover", event => {
    event.preventDefault();
    arquivoZone.classList.add("drag-over");
  });

  arquivoZone.addEventListener("dragleave", () => {
    arquivoZone.classList.remove("drag-over");
  });

  arquivoZone.addEventListener("drop", event => {
    event.preventDefault();
    arquivoZone.classList.remove("drag-over");
    if (event.dataTransfer?.files?.length) {
      arquivoInput.files = event.dataTransfer.files;
      arquivoInput.dispatchEvent(new Event("change"));
    }
  });

  arquivoInput.addEventListener("change", updateInfo);

  processBtn?.addEventListener("click", event => {
    event.preventDefault();
    if (!arquivoInput.files.length) {
      arquivoZone.classList.add("drag-over");
      setTimeout(() => arquivoZone.classList.remove("drag-over"), 600);
      return;
    }
    show(spinner);
    btnText.textContent = "Processando...";
    processBtn.disabled = true;
    setTimeout(() => form.submit(), 350);
  });
});

