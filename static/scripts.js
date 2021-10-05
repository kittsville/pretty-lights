const white = chroma('white');
const black = chroma('black');
const statusBar = document.getElementById('status');
const addStatus = statusText => {
  const status = document.createElement('em');
  status.textContent = statusText;
  statusBar.appendChild(status);

  setTimeout(() => {statusBar.removeChild(status)}, 3000);
}

const convertColor = colour => {
  const [rawHue, rawSat, rawLum] = colour.hsv();

  const hue = isNaN(rawHue) ? 0 : Math.round((rawHue / 360) * 255);
  const sat = Math.round(rawSat * 255);
  const lum = Math.round(rawLum * 255);

  return {hue, sat, lum};
}

const sendColors = colours => {
  const url = `/lights`;
  fetch(url, {
    method  : 'POST',
    body    : JSON.stringify(colours),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => addStatus(response.statusText))
    .catch(e => addStatus('Error: ' + e));
}

document.getElementById('custom-color').addEventListener('input', ev => sendColors([convertColor(chroma(ev.target.value))]));

document.querySelectorAll('button').forEach(button => {
  const colors = button.getAttribute('colors').split(',').map(c => convertColor(chroma(c)));

  button.addEventListener('click', () => {
    sendColors(colors);

    button.blur();
  });
});

const colorButtons = async function() {
  document.querySelectorAll('button').forEach(button => {
    const colors = button.getAttribute('colors').split(',').map(c => chroma(c));

    if (colors.length == 1) {
      button.style.backgroundColor = colors[0].css();

      // This is unnecessarily complicated but I loved writing it
      // Should probably just use CSS so the colours don't 'pop' into place
      button.style.color = chroma.contrast(colors[0], white) > chroma.contrast(colors[0], black) ? white.css() : black.css();
      button.style.border = 'none';
    }
  });
}

colorButtons();
