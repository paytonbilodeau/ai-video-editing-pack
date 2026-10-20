import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';
import {loadFont} from '@remotion/fonts';

// Headless Chrome has NO system fonts. Every font must be loaded here.
const loading = delayRender('Loading fonts');
Promise.all([
  loadFont({
    family: 'Departure Mono',
    url: staticFile('fonts/DepartureMono-Regular.woff2'),
    weight: '400',
  }),
  loadFont({
    family: 'Instrument Serif',
    url: staticFile('fonts/InstrumentSerif-Italic.woff2'),
    weight: '400',
    style: 'italic',
  }),
])
  .then(() => continueRender(loading))
  .catch((err) => cancelRender(err));

// The signature pixel-mono face (MIT, bundled in public/fonts/)
export const pixel = '"Departure Mono", monospace';
// Serif italic for small conversational asides ("= risk of death")
export const serifItalic = '"Instrument Serif", serif';
