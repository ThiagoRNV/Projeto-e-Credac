document.addEventListener("DOMContentLoaded", () => {
    const spedInput = document.getElementById("sped_files");
    const folderInput = document.getElementById("folder_input");
    const spedZone = document.getElementById("spedZone");
    const xmlZone = document.getElementById("xmlZone");
    const spedInfo = document.getElementById("spedInfo");
    const folderInfo = document.getElementById("folderInfo");
    const xmlCard = document.getElementById("xmlCard");
    const processBtnContainer = document.getElementById("processBtnRow");
    const processBtn = document.getElementById("processBtn");
    const form = document.getElementById("formArquivos");
  
    const show = el => el && el.classList.remove("d-none");
    const hide = el => el && el.classList.add("d-none");
  
    // Função para atualizar a visibilidade do botão de processar
    function updateProcessButton() {
      const hasSped = spedInput && spedInput.files.length > 0;
      const hasXml = folderInput && folderInput.files.length > 0 && 
                     Array.from(folderInput.files).some(f => f.name.toLowerCase().endsWith(".xml"));
      
      if (hasSped && hasXml && processBtnContainer) {
        show(processBtnContainer);
      } else if (processBtnContainer) {
        hide(processBtnContainer);
      }
    }
  
    function setupDropZone(zone, input, callback) {
      zone.addEventListener("click", () => input.click());
      zone.addEventListener("dragover", e => {
        e.preventDefault();
        zone.classList.add("drag-over");
      });
      zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
      zone.addEventListener("drop", e => {
        e.preventDefault();
        zone.classList.remove("drag-over");
        input.files = e.dataTransfer.files;
        input.dispatchEvent(new Event("change"));
        callback();
      });
    }
  
    if (spedZone && spedInput) {
      setupDropZone(spedZone, spedInput, () => {});
    }
    
    if (xmlZone && folderInput) {
      setupDropZone(xmlZone, folderInput, () => {});
    }
  
    if (spedInput) {
      spedInput.addEventListener("change", () => {
        if (spedInput.files.length > 0) {
          if (spedInfo) {
            show(spedInfo);
            spedInfo.innerHTML = `🧾 ${spedInput.files[0].name}`;
          }
          // Sempre mostra o card XML quando SPED é selecionado
          if (xmlCard) {
            show(xmlCard);
          }
        } else {
          if (spedInfo) hide(spedInfo);
          // Não esconde o card XML se houver arquivos XML selecionados
          const hasXml = folderInput && folderInput.files.length > 0 && 
                         Array.from(folderInput.files).some(f => f.name.toLowerCase().endsWith(".xml"));
          if (xmlCard && !hasXml) {
            hide(xmlCard);
          }
        }
        // Atualiza o botão de processar
        updateProcessButton();
      });
    }

    if (folderInput) {
      folderInput.addEventListener("change", () => {
        const xmlFiles = Array.from(folderInput.files).filter(f => f.name.toLowerCase().endsWith(".xml"));
        if (xmlFiles.length > 0) {
          // Garante que o card XML esteja sempre visível quando há arquivos XML
          if (xmlCard) {
            show(xmlCard);
          }
          if (folderInfo) {
            show(folderInfo);
            folderInfo.innerHTML = `📂 ${xmlFiles.length} arquivo(s) XML selecionado(s)`;
          }
        } else {
          if (folderInfo) hide(folderInfo);
          // Só esconde o card XML se não houver SPED selecionado
          const hasSped = spedInput && spedInput.files.length > 0;
          if (xmlCard && !hasSped) {
            hide(xmlCard);
          }
        }
        // Atualiza o botão de processar
        updateProcessButton();
      });
    }
  
  
    const btnSpinner = document.getElementById("spinnerNFe");
    const btnLabel = document.getElementById("btnTextNFe");

    processBtn?.addEventListener("click", e => {
      e.preventDefault();
      show(btnSpinner);
      if (btnLabel) btnLabel.textContent = "Processando...";
      processBtn.disabled = true;

      // form.submit() não envia o name/value do botão, então incluímos manualmente
      if (form && !form.querySelector("input[name='btn']")) {
        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "btn";
        hidden.value = processBtn.value;
        form.appendChild(hidden);
      }

      setTimeout(() => {
        if (form) form.submit();
      }, 400);
    });

    // Verificação inicial: se já houver arquivos selecionados, mostra os cards apropriados
    if (spedInput && spedInput.files.length > 0) {
      if (spedInfo) {
        show(spedInfo);
        spedInfo.innerHTML = `🧾 ${spedInput.files[0].name}`;
      }
      if (xmlCard) {
        show(xmlCard);
      }
    }

    if (folderInput && folderInput.files.length > 0) {
      const xmlFiles = Array.from(folderInput.files).filter(f => f.name.toLowerCase().endsWith(".xml"));
      if (xmlFiles.length > 0) {
        if (xmlCard) {
          show(xmlCard);
        }
        if (folderInfo) {
          show(folderInfo);
          folderInfo.innerHTML = `📂 ${xmlFiles.length} arquivo(s) XML selecionado(s)`;
        }
      }
    }

    // Atualiza o botão de processar no carregamento inicial
    updateProcessButton();
  });