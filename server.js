// server.js
const express = require('express');
const cors = require('cors');
const app = express();
app.use(cors());

// Initialize relays: {1:{on:false,brightness:0},…}
const relays = {1:{on:false,brightness:0},2:{on:false,brightness:0},
                3:{on:false,brightness:0},4:{on:false,brightness:0}};

// Turn on/off: GET /relay/:id/:cmd (cmd = on|off)
app.get('/relay/:id/:cmd', (req, res) => {
  const id = +req.params.id, cmd = req.params.cmd;
  if (!relays[id] || !['on','off'].includes(cmd))
    return res.status(400).json({error:'invalid'});
  relays[id].on = (cmd==='on');
  console.log(`Relay ${id} → ${cmd.toUpperCase()}`);
  res.json({id, ...relays[id]});
});

// Set brightness: GET /relay/:id/brightness/:value (0–100)
app.get('/relay/:id/brightness/:val', (req, res) => {
  const id = +req.params.id, val = +req.params.val;
  if (!relays[id] || val<0 || val>100)
    return res.status(400).json({error:'invalid'});
  relays[id].brightness = val;
  relays[id].on = val>0;
  console.log(`Relay ${id} → BRIGHTNESS ${val}%`);
  res.json({id, ...relays[id]});
});

// Status: GET /status
app.get('/status', (req, res) => res.json(relays));

const PORT = 3000;
app.listen(PORT, () => console.log(`Mock server on http://localhost:${PORT}`));
