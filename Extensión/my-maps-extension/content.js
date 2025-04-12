console.log("My Maps Content Script cargado.");

// Escucha mensajes desde el popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "RUN_MARKER_PROCESS") {
    console.log("Recibida acción RUN_MARKER_PROCESS desde popup");
    processMarkers();
  }
});

// Función para simular un clic “real”
function simulateRealClick(element) {
  const mouseDown = new MouseEvent("mousedown", { bubbles: true, cancelable: true });
  const mouseUp = new MouseEvent("mouseup", { bubbles: true, cancelable: true });
  const mouseClick = new MouseEvent("click", { bubbles: true, cancelable: true });
  element.dispatchEvent(mouseDown);
  element.dispatchEvent(mouseUp);
  element.dispatchEvent(mouseClick);
}

// Función principal
async function processMarkers() {
  console.log("Iniciando proceso de marcadores...");
  
  // Selecciona todos los marcadores
  const markers = document.querySelectorAll('#ly0-layer-items-container > div[fl_id]');
  console.log("Marcadores encontrados:", markers.length);
  
  for (const marker of markers) {
    const fl_id = marker.getAttribute('fl_id');
    console.log("Procesando marcador con fl_id:", fl_id);

    // 1. Simula clic en el marcador
    simulateRealClick(marker);

    // 2. Espera para que se abra y renderice el infowindow
    await new Promise(resolve => setTimeout(resolve, 2000));

    // 3. Localiza el contenedor del infowindow
    const infowindowEl = document.querySelector('#map-infowindow-content');
    if (!infowindowEl) {
      console.warn(`Marcador ${fl_id}: No se encontró el contenedor del infowindow.`);
    } else {
      // Busca un <a> dentro del infowindow para extraer la URL
      let linkEl = infowindowEl.querySelector('a');
      let url = linkEl ? linkEl.href : null;

      // Descartar si no existe URL o si es de Google Maps
      if (!url || url.includes('maps.google.') || url.includes('google.com/maps')) {
        console.warn(`Marcador ${fl_id}: URL nula o de Google Maps (descartada).`);
        url = null; 
      }

      if (!url) {
        // No hay URL válida => no editamos nada
        console.warn(`Marcador ${fl_id}: No se encontró ninguna URL válida, no se edita descripción.`);
      } else {
        console.log(`Marcador ${fl_id}: URL extraída: ${url}`);

        // 4. Haz clic en el botón "Editar"
        const editBtn = document.querySelector('#map-infowindow-edit-button');
        if (editBtn) {
          simulateRealClick(editBtn);
          // Esperamos un poco para entrar en modo edición
          await new Promise(r => setTimeout(r, 1000));

          // 5. Pega la URL en el campo de descripción sin borrar lo existente,
          //    salvo que sea exactamente la misma
          const descInput = document.querySelector('#map-infowindow-attr-descripción-value');
          if (descInput) {
            console.log(`Marcador ${fl_id}: Campo descripción encontrado, intentando añadir URL...`);

            // Obtenemos el texto existente (puede estar en value o en textContent si es contenteditable)
            const oldDescValue = descInput.value || "";
            const oldDescText = descInput.textContent || "";

            // Para comparar con la URL, usamos trim() para quitar espacios en blanco extremos
            const oldDescValueTrim = oldDescValue.trim();
            const oldDescTextTrim = oldDescText.trim();
            const urlTrim = url.trim();

            // Verificamos si lo que hay ES exactamente la misma URL
            if (oldDescValueTrim === urlTrim || oldDescTextTrim === urlTrim) {
              console.log(`Marcador ${fl_id}: La descripción ya es exactamente la URL. No se añade nada.`);
            } else {
              // Añadimos la URL al final, con un salto de línea si ya había texto
              const separatorValue = oldDescValueTrim ? "\n" : "";
              const newDescValue = oldDescValue + separatorValue + url;

              const separatorText = oldDescTextTrim ? "\n" : "";
              const newDescText = oldDescText + separatorText + url;

              // Asignamos al .value (para <textarea>/<input>)
              descInput.focus();
              descInput.value = newDescValue;
              descInput.dispatchEvent(new Event('input', { bubbles: true }));
              descInput.dispatchEvent(new Event('change', { bubbles: true }));

              // Por si fuese un div[contenteditable]
              descInput.textContent = newDescText;
              descInput.dispatchEvent(new Event('input', { bubbles: true }));
              descInput.dispatchEvent(new Event('change', { bubbles: true }));

              descInput.blur();

              console.log(`Marcador ${fl_id}: Descripción actualizada con la nueva URL.`);

              // 6. Pulsa "Guardar"
              const saveButton = document.querySelector('#map-infowindow-done-editing-button > div');
              if (saveButton) {
                simulateRealClick(saveButton);
                console.log(`Marcador ${fl_id}: Guardado tras añadir URL.`);
                await new Promise(r => setTimeout(r, 1000));
              } else {
                console.warn(`Marcador ${fl_id}: No se encontró el botón de guardar.`);
              }
            }
          } else {
            console.warn(`Marcador ${fl_id}: No se encontró el campo de descripción.`);
          }
        } else {
          console.warn(`Marcador ${fl_id}: No se encontró el botón de editar.`);
        }
      }
    }

    // 7. Cierra el infowindow con Escape
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    console.log(`Marcador ${fl_id}: Infowindow cerrado con Escape.`);

    // Espera breve antes de pasar al siguiente
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log("Proceso completado");
}
