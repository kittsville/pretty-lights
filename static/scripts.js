const statusBar = document.getElementById('status');
const addStatus = statusText => {
  const status = document.createElement('em');
  status.textContent = statusText;
  statusBar.appendChild(status);

}

const sendColor = rawColor => {
  const colour = chroma(rawColor);

  const [rawHue, rawSat, rawLum] = colour.hsv();

  const hue = isNaN(rawHue) ? 0 : Math.round((rawHue / 360) * 255);
  const sat = Math.round(rawSat * 255);
  const lum = Math.round(rawLum * 255);

  console.log(`Sending HSV(${hue}, ${sat}, ${lum})`);

  const url = `/lights?hue=${hue}&sat=${sat}&lum=${lum}`;
  fetch(url, {method: 'POST'})
    .then(response => addStatus(response.statusText))
    .catch(e => addStatus('Error: ' + e));
}

document.getElementById('custom-color').addEventListener('change', ev => sendColor(ev.target.value));

document.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
  sendColor(button.getAttribute('color'));

  button.blur();
}));
