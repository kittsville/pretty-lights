const statusBar = document.getElementById('status');
const addStatus = statusText => {
  const status = document.createElement('em');
  status.textContent = statusText;
  statusBar.appendChild(status);

}

const sendColors = rawColors => {
  const colours = rawColors.map(rawColor => {
    const colour = chroma(rawColor);

    const [rawHue, rawSat, rawLum] = colour.hsv();

    const hue = isNaN(rawHue) ? 0 : Math.round((rawHue / 360) * 255);
    const sat = Math.round(rawSat * 255);
    const lum = Math.round(rawLum * 255);

    console.log(`Sending HSV(${hue}, ${sat}, ${lum})`);

    return {hue, sat, lum};
  });

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

document.getElementById('custom-color').addEventListener('input', ev => sendColors([ev.target.value]));

document.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
  sendColors(button.getAttribute('colors').split(','));

  button.blur();
}));
