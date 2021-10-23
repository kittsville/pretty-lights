const NUM_COLUMNS = 5;
const NUM_LEDS    = 100;
const white = chroma('white');
const black = chroma('black');
const statusBar = document.getElementById('status');
const addStatus = statusText => {
  const status = document.createElement('em');
  status.textContent = statusText;
  statusBar.appendChild(status);

  setTimeout(() => {status.classList.add('disappearing')}, 2000);
  setTimeout(() => {statusBar.removeChild(status)}, 3000);
}

const convertColor = color => {
  const [rawHue, rawSat, rawLum] = color.hsv();

  const hue = isNaN(rawHue) ? 0 : Math.round((rawHue / 360) * 255);
  const sat = Math.round(rawSat * 255);
  const lum = Math.round(rawLum * 255);

  return {hue, sat, lum};
}

const sendColors = (colors, multiplier) => {
  const payload = {multiplier, colors}

  const url = `lights`;
  fetch(url, {
    method  : 'POST',
    body    : JSON.stringify(payload),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => addStatus(response.statusText))
    .catch(e => addStatus('Error: ' + e));
}

document.getElementById('custom-color').addEventListener(
  'input',
  ev => sendColors([convertColor(chroma(ev.target.value))])
);

document.getElementById('random').addEventListener('click', () => {
  const url = `random`;
  fetch(url, { method : 'POST' })
    .then(response => addStatus(response.statusText))
    .catch(e => addStatus('Error: ' + e));
});

document.getElementById('random-multicolored').addEventListener('click', () => {
  sendColors(
    ColorTools.gradient(...ColorTools.randomPastels(2), NUM_COLUMNS).map(convertColor),
    "columns"
  );
});

document.getElementById('random-multicolored-bars').addEventListener('click', () => {
  sendColors(
    ColorTools.gradient(...ColorTools.randomPastels(2), NUM_LEDS).map(convertColor),
    1
  );
});

document.querySelectorAll('button[colors]').forEach(button => {
  const colors        = button.getAttribute('colors').split(',').map(c => convertColor(chroma(c)));
  const rawMultiplier = button.getAttribute('multiplier');
  const multiplier    = rawMultiplier ? parseInt(rawMultiplier, 10) : 'columns';

  button.addEventListener('click', () => {
    sendColors(colors, multiplier);

    button.blur();
  });
});

const colorButtons = async function() {
  document.querySelectorAll('button[colors]').forEach(button => {
    const colors = button.getAttribute('colors').split(',').map(c => chroma(c));

    if (colors.length == 1) {
      button.style.backgroundColor = colors[0].css();

      // This is unnecessarily complicated but I loved writing it
      // Should probably just use CSS so the colors don't 'pop' into place
      button.style.color = chroma.contrast(colors[0], white) > chroma.contrast(colors[0], black) ? white.css() : black.css();
      button.style.border = 'none';
    }
  });
}

colorButtons();

// Source: https://github.com/kittsville/pride-flag-generator/blob/5f3b26270a6032185dd89197b248cc60c224500f/assets/definitions.js
class ColorTools {
  static log(color) {
    console.log('%c                       ', `background: ${color}`);
  }

  static gradient(firstColor, secondColor, numberOfParts) {
    if (numberOfParts < 2) {
      throw `Gradients require at least two parts, [${numberOfParts}] given'`
    }

    const scale = chroma.scale([firstColor, secondColor]).mode('lab');
    const step = 1 / (numberOfParts - 1);

    return Array.from({length: numberOfParts}, (_, i) => scale(step * i));
  }

  static twoPartGradient(firstColor, secondColor, thirdColor, numberOfParts) {
    const firstGradient = ColorTools.gradient(firstColor, secondColor, numberOfParts);
    const secondGradient = ColorTools.gradient(secondColor, thirdColor, numberOfParts);

    return firstGradient.concat(secondGradient.slice(1));
  }

  static randomHue() {
    return 360 * Math.random();
  }

  static hueDistance(hue1, hue2) {
    return Math.min(Math.abs(hue1 - hue2), (Math.min(hue1, hue2) + 360) - Math.max(hue1, hue2))
  }

  static randomPastels(number) {
    let pastels = [];
    let attempts = 0;
    const limit = number * 50;
    const separation = 70;

    do {
      attempts++;

      const hue = ColorTools.randomHue();

      if (!pastels.some(el => ColorTools.hueDistance(hue, el) <= separation)) {
        pastels.push(hue);
      }
    } while (pastels.length < number && attempts <= limit)

    if (attempts >= limit) {
      console.log(`Gave up generating distinctive colours after ${attempts} attempts`);
    }

    return pastels.map(hue => `hsl(${hue},100%,50%)`);
  }
}
