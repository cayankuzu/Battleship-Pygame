const canvas = document.querySelector("#game");
const context = canvas.getContext("2d");

const WIDTH = 1260;
const HEIGHT = 960;
const CELL = 50;
const GRID = 10;
const PLAYER_GRID = { x: 50, y: 50 };
const COMPUTER_GRID = { x: 760, y: 50 };
const BUTTON_Y = 900;

const fleetSpec = [
  {
    id: "carrier",
    name: "carrier",
    size: 5,
    image: "assets/images/ships/carrier/carrier.png",
    start: { x: 50, y: 600 },
    pixels: { width: 45, height: 245 },
  },
  {
    id: "battleship",
    name: "battleship",
    size: 4,
    image: "assets/images/ships/battleship/battleship.png",
    start: { x: 125, y: 600 },
    pixels: { width: 40, height: 195 },
  },
  {
    id: "cruiser",
    name: "cruiser",
    size: 4,
    image: "assets/images/ships/cruiser/cruiser.png",
    start: { x: 200, y: 600 },
    pixels: { width: 40, height: 195 },
  },
  {
    id: "destroyer",
    name: "destroyer",
    size: 4,
    image: "assets/images/ships/destroyer/destroyer.png",
    start: { x: 275, y: 600 },
    pixels: { width: 43, height: 195 },
  },
  {
    id: "submarine",
    name: "submarine",
    size: 3,
    image: "assets/images/ships/submarine/submarine.png",
    start: { x: 350, y: 600 },
    pixels: { width: 30, height: 145 },
  },
  {
    id: "patrol",
    name: "patrol boat",
    size: 2,
    image: "assets/images/ships/patrol boat/patrol boat.png",
    start: { x: 425, y: 600 },
    pixels: { width: 20, height: 95 },
  },
  {
    id: "rescue",
    name: "rescue ship",
    size: 2,
    image: "assets/images/ships/rescue ship/rescue ship.png",
    start: { x: 500, y: 600 },
    pixels: { width: 20, height: 95 },
  },
];

const assets = {
  background: "assets/images/background/gamebg.png",
  playerGrid: "assets/images/grids/player_grid.png",
  computerGrid: "assets/images/grids/comp_grid.png",
  button: "assets/images/buttons/button.png",
  miss: "assets/images/tokens/redtoken.png",
  hit: "assets/images/tokens/greentoken.png",
};

const tracks = [
  "Black_Sabbath__War_Pigs.mp3",
  "Iron_Maiden__The_Trooper.mp3",
  "Metallica__One.mp3",
  "Cannibal_Corpse__The_Time_To_Kill_Is_Now.mp3",
  "Megadeth __ Holy_Wars.mp3",
  "Megadeth__Symphony_Of_Destruction.mp3",
];

const images = new Map();
const audio = {
  music: new Audio(),
  splash: new Audio("assets/sounds/splash.wav"),
  explosion: new Audio("assets/sounds/explosion.wav"),
  gunshot: new Audio("assets/sounds/gunshot.wav"),
};

let musicIndex = 0;
let musicVolume = 0.3;
let splashVolume = 0.05;
let explosionVolume = 0.05;
let gunshotVolume = 0.05;
let musicStarted = false;

let playerBoard;
let computerBoard;
let playerFleet;
let computerFleet;
let phase;
let playerTurn;
let gameOver;
let winner;
let dragging;
let pointer;
let statusMessage;
let playerStats;
let computerStats;
let shotAnimations;

const mainButtons = [
  { name: "Randomize", x: 25, y: BUTTON_Y, width: 150, height: 50 },
  { name: "Reset", x: 200, y: BUTTON_Y, width: 150, height: 50 },
  { name: "Start", x: 375, y: BUTTON_Y, width: 150, height: 50 },
  { name: "Quit", x: 550, y: BUTTON_Y, width: 150, height: 50 },
];

const musicButtons = [
  { name: "Prev", x: 760, y: 715, width: 80, height: 30 },
  { name: "PlayPause", x: 850, y: 715, width: 100, height: 30 },
  { name: "Next", x: 960, y: 715, width: 80, height: 30 },
  { name: "Vol-", x: 1050, y: 715, width: 80, height: 30 },
  { name: "Vol+", x: 1140, y: 715, width: 80, height: 30 },
];

const sfxButtons = [
  { name: "Splash_VolDown", x: 510, y: 730, width: 50, height: 30 },
  { name: "Splash_VolUp", x: 680, y: 730, width: 50, height: 30 },
  { name: "Explosion_VolDown", x: 510, y: 790, width: 50, height: 30 },
  { name: "Explosion_VolUp", x: 680, y: 790, width: 50, height: 30 },
  { name: "Gunshot_VolDown", x: 510, y: 850, width: 50, height: 30 },
  { name: "Gunshot_VolUp", x: 680, y: 850, width: 50, height: 30 },
];

function loadImage(source) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      images.set(source, image);
      resolve(image);
    };
    image.onerror = reject;
    image.src = source;
  });
}

function preload() {
  const sources = [
    ...Object.values(assets),
    ...fleetSpec.map((ship) => ship.image),
  ];
  return Promise.all(sources.map(loadImage));
}

function emptyBoard() {
  return Array.from({ length: GRID }, () => Array(GRID).fill(null));
}

function makeShip(spec) {
  return {
    ...spec,
    x: spec.start.x,
    y: spec.start.y,
    horizontal: false,
    row: null,
    column: null,
    placed: false,
    hits: new Set(),
    sunk: false,
  };
}

function cellsFor(ship, row = ship.row, column = ship.column) {
  return Array.from({ length: ship.size }, (_, offset) => ({
    row: row + (ship.horizontal ? 0 : offset),
    column: column + (ship.horizontal ? offset : 0),
  }));
}

function canPlace(ship, row, column, board, fleet = []) {
  const cells = cellsFor(ship, row, column);
  if (
    cells.some(
      (cell) =>
        cell.row < 0 ||
        cell.column < 0 ||
        cell.row >= GRID ||
        cell.column >= GRID,
    )
  ) {
    return false;
  }

  return cells.every(({ row: cellRow, column: cellColumn }) => {
    const occupant = board[cellRow][cellColumn];
    return !occupant || occupant === ship.id;
  });
}

function clearShipFromBoard(ship, board) {
  for (let row = 0; row < GRID; row += 1) {
    for (let column = 0; column < GRID; column += 1) {
      if (board[row][column] === ship.id) board[row][column] = null;
    }
  }
}

function placeShip(ship, row, column, board) {
  clearShipFromBoard(ship, board);
  if (!canPlace(ship, row, column, board)) return false;
  ship.row = row;
  ship.column = column;
  ship.placed = true;
  cellsFor(ship).forEach(({ row: cellRow, column: cellColumn }) => {
    board[cellRow][cellColumn] = ship.id;
  });
  ship.x = PLAYER_GRID.x + column * CELL + CELL / 2;
  ship.y = PLAYER_GRID.y + row * CELL + CELL / 2;
  return true;
}

function randomizeFleet(fleet, board, isPlayer) {
  for (let row = 0; row < GRID; row += 1) board[row].fill(null);

  fleet.forEach((ship) => {
    let placed = false;
    let attempts = 0;
    while (!placed && attempts < 5000) {
      ship.horizontal = Math.random() > 0.5;
      const maximumRow = GRID - (ship.horizontal ? 1 : ship.size);
      const maximumColumn = GRID - (ship.horizontal ? ship.size : 1);
      const row = Math.floor(Math.random() * (maximumRow + 1));
      const column = Math.floor(Math.random() * (maximumColumn + 1));
      placed = canPlace(ship, row, column, board);
      if (placed) {
        ship.row = row;
        ship.column = column;
        ship.placed = true;
        cellsFor(ship).forEach(({ row: cellRow, column: cellColumn }) => {
          board[cellRow][cellColumn] = ship.id;
        });
        if (isPlayer) {
          ship.x = PLAYER_GRID.x + column * CELL + CELL / 2;
          ship.y = PLAYER_GRID.y + row * CELL + CELL / 2;
        }
      }
      attempts += 1;
    }
  });
}

function resetGame() {
  playerBoard = emptyBoard();
  computerBoard = emptyBoard();
  playerFleet = fleetSpec.map(makeShip);
  computerFleet = fleetSpec.map(makeShip);
  randomizeFleet(computerFleet, computerBoard, false);
  phase = "deployment";
  playerTurn = true;
  gameOver = false;
  winner = "";
  dragging = null;
  pointer = { x: 0, y: 0 };
  statusMessage = "Place your ships, then press Start";
  playerStats = { shots: 0, hits: 0, misses: 0, sunk: 0 };
  computerStats = { shots: 0, hits: 0, misses: 0, sunk: 0 };
  shotAnimations = [];
}

function playSound(name) {
  const sound = audio[name];
  sound.currentTime = 0;
  sound.volume =
    name === "splash"
      ? splashVolume
      : name === "explosion"
        ? explosionVolume
        : gunshotVolume;
  sound.play().catch(() => {});
}

function setTrack(index) {
  musicIndex = (index + tracks.length) % tracks.length;
  audio.music.src = `assets/sounds/${encodeURIComponent(tracks[musicIndex]).replace(/%2F/g, "/")}`;
  audio.music.loop = true;
  audio.music.volume = musicVolume;
  if (musicStarted) audio.music.play().catch(() => {});
}

function toggleMusic() {
  if (!musicStarted) {
    musicStarted = true;
    setTrack(musicIndex);
    audio.music.play().catch(() => {});
    return;
  }
  if (audio.music.paused) audio.music.play().catch(() => {});
  else audio.music.pause();
}

function roundedRect(x, y, width, height, radius) {
  context.beginPath();
  context.roundRect(x, y, width, height, radius);
}

function drawButton(button, label = button.name) {
  const buttonImage = images.get(assets.button);
  context.drawImage(buttonImage, button.x, button.y, button.width, button.height);
  context.fillStyle = "#fff";
  context.font = "bold 15px Arial";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(label, button.x + button.width / 2, button.y + button.height / 2);
}

function drawText(text, x, y, size = 14, color = "#fff", align = "left") {
  context.fillStyle = color;
  context.font = `bold ${size}px "Courier New", monospace`;
  context.textAlign = align;
  context.textBaseline = "alphabetic";
  context.fillText(text, x, y);
}

function drawBackground() {
  context.drawImage(images.get(assets.background), 0, 0, WIDTH, HEIGHT);
  context.drawImage(images.get(assets.playerGrid), 0, 0, 550, 550);
  context.drawImage(images.get(assets.computerGrid), 710, 0, 550, 550);
}

function shipDrawSize(ship) {
  return ship.horizontal
    ? { width: ship.pixels.height, height: ship.pixels.width }
    : { width: ship.pixels.width, height: ship.pixels.height };
}

function shipDrawPosition(ship) {
  const size = shipDrawSize(ship);
  if (!ship.placed || (dragging && dragging.ship.id === ship.id)) {
    return { x: ship.x, y: ship.y, ...size };
  }

  return {
    x:
      PLAYER_GRID.x +
      ship.column * CELL +
      (ship.horizontal ? 2 : (CELL - size.width) / 2),
    y:
      PLAYER_GRID.y +
      ship.row * CELL +
      (ship.horizontal ? (CELL - size.height) / 2 : 2),
    ...size,
  };
}

function drawShip(ship) {
  const image = images.get(ship.image);
  const position = shipDrawPosition(ship);
  context.save();
  if (ship.horizontal) {
    context.translate(position.x + position.width / 2, position.y + position.height / 2);
    context.rotate(Math.PI / 2);
    context.drawImage(
      image,
      -position.height / 2,
      -position.width / 2,
      position.height,
      position.width,
    );
  } else {
    context.drawImage(
      image,
      position.x,
      position.y,
      position.width,
      position.height,
    );
  }
  context.restore();

  if (phase === "deployment") {
    context.strokeStyle = "#ff2525";
    context.lineWidth = 1;
    context.strokeRect(position.x, position.y, position.width, position.height);
  }
}

function drawPlayerFleet() {
  playerFleet.forEach(drawShip);
}

function drawShots(board, isPlayerBoard) {
  for (let row = 0; row < GRID; row += 1) {
    for (let column = 0; column < GRID; column += 1) {
      const cell = board[row][column];
      if (!cell || typeof cell !== "object" || !cell.shot) continue;
      const grid = isPlayerBoard ? PLAYER_GRID : COMPUTER_GRID;
      const image = images.get(cell.hit ? assets.hit : assets.miss);
      context.drawImage(
        image,
        grid.x + column * CELL,
        grid.y + row * CELL,
        CELL,
        CELL,
      );
    }
  }
}

function drawScoreboard() {
  context.fillStyle = "rgba(28, 28, 28, 0.88)";
  context.fillRect(750, 600, 510, 42);
  const remainingPlayer = playerFleet.filter((ship) => !ship.sunk).length;
  const remainingComputer = computerFleet.filter((ship) => !ship.sunk).length;
  drawText(
    `Player - Shots: ${playerStats.shots}  Hits: ${playerStats.hits}  Misses: ${playerStats.misses}  Sunk: ${playerStats.sunk}  Remaining: ${remainingPlayer}`,
    756,
    617,
    12,
  );
  drawText(
    `Computer - Shots: ${computerStats.shots}  Hits: ${computerStats.hits}  Misses: ${computerStats.misses}  Sunk: ${computerStats.sunk}  Remaining: ${remainingComputer}`,
    756,
    636,
    12,
  );
}

function drawTurn() {
  const label =
    phase === "deployment"
      ? statusMessage
      : gameOver
        ? `${winner} Wins!`
        : playerTurn
          ? "Your Turn"
          : "Thinking...";
  drawText(label, 1005, 582, 18, "#111", "center");
}

function drawSfxPanel() {
  context.fillStyle = "rgba(30,30,30,0.92)";
  context.fillRect(500, 710, 240, 180);
  sfxButtons.forEach((button) => {
    context.fillStyle = "#555";
    context.fillRect(button.x, button.y, button.width, button.height);
    drawText(
      button.name.endsWith("VolDown") ? "-" : "+",
      button.x + button.width / 2,
      button.y + 21,
      15,
      "#fff",
      "center",
    );
  });
  drawText(`Splash: ${splashVolume.toFixed(2)}`, 570, 750, 12);
  drawText(`Explosion: ${explosionVolume.toFixed(2)}`, 570, 810, 12);
  drawText(`Gunshot: ${gunshotVolume.toFixed(2)}`, 570, 870, 12);
}

function drawMusicPlayer() {
  musicButtons.forEach((button) => {
    context.fillStyle = "#444";
    context.fillRect(button.x, button.y, button.width, button.height);
    drawText(
      button.name,
      button.x + button.width / 2,
      button.y + 20,
      12,
      "#fff",
      "center",
    );
  });

  tracks.forEach((track, index) => {
    drawText(
      track,
      760,
      780 + index * 24,
      12,
      index === musicIndex ? "#fff" : "#dedede",
    );
  });
}

function drawOverlay() {
  if (!gameOver) return;
  context.fillStyle = "rgba(0,0,0,0.72)";
  context.fillRect(0, 0, WIDTH, HEIGHT);
  drawText(`${winner} Wins!`, WIDTH / 2, HEIGHT / 2 - 100, 46, "#fff", "center");
  drawButton(
    { name: "Restart", x: WIDTH / 2 - 160, y: HEIGHT / 2 + 50, width: 150, height: 50 },
    "Restart",
  );
  drawButton(
    { name: "Quit", x: WIDTH / 2 + 10, y: HEIGHT / 2 + 50, width: 150, height: 50 },
    "Quit",
  );
}

function render() {
  drawBackground();
  drawPlayerFleet();
  drawShots(playerBoard, true);
  drawShots(computerBoard, false);
  drawTurn();
  drawScoreboard();
  drawSfxPanel();
  drawMusicPlayer();
  mainButtons.forEach((button) => drawButton(button));
  drawOverlay();
  window.requestAnimationFrame(render);
}

function pointFromEvent(event) {
  const bounds = canvas.getBoundingClientRect();
  return {
    x: ((event.clientX - bounds.left) / bounds.width) * WIDTH,
    y: ((event.clientY - bounds.top) / bounds.height) * HEIGHT,
  };
}

function contains(rect, point) {
  return (
    point.x >= rect.x &&
    point.x <= rect.x + rect.width &&
    point.y >= rect.y &&
    point.y <= rect.y + rect.height
  );
}

function shipAt(point) {
  return [...playerFleet].reverse().find((ship) => contains(shipDrawPosition(ship), point));
}

function findShip(fleet, id) {
  return fleet.find((ship) => ship.id === id);
}

function fireAt(board, fleet, row, column, stats) {
  if (typeof board[row][column] === "object" && board[row][column]?.shot) return null;

  const shipId = board[row][column];
  stats.shots += 1;
  playSound("gunshot");

  if (shipId) {
    const ship = findShip(fleet, shipId);
    const key = `${row}-${column}`;
    ship.hits.add(key);
    board[row][column] = { shipId, shot: true, hit: true };
    stats.hits += 1;
    playSound("explosion");
    if (ship.hits.size === ship.size) {
      ship.sunk = true;
      stats.sunk += 1;
    }
    return { hit: true, ship };
  }

  board[row][column] = { shot: true, hit: false };
  stats.misses += 1;
  playSound("splash");
  return { hit: false, ship: null };
}

function checkGameOver() {
  if (computerFleet.every((ship) => ship.sunk)) {
    gameOver = true;
    winner = "Player";
    return true;
  }
  if (playerFleet.every((ship) => ship.sunk)) {
    gameOver = true;
    winner = "Computer";
    return true;
  }
  return false;
}

function computerAttack() {
  if (gameOver || phase !== "battle") return;
  const choices = [];
  for (let row = 0; row < GRID; row += 1) {
    for (let column = 0; column < GRID; column += 1) {
      if (!(typeof playerBoard[row][column] === "object" && playerBoard[row][column]?.shot)) {
        choices.push({ row, column });
      }
    }
  }
  const target = choices[Math.floor(Math.random() * choices.length)];
  fireAt(playerBoard, playerFleet, target.row, target.column, computerStats);
  if (!checkGameOver()) playerTurn = true;
}

function startBattle() {
  if (!playerFleet.every((ship) => ship.placed)) {
    statusMessage = "Place every ship before Start";
    return;
  }
  phase = "battle";
  playerTurn = true;
}

function handleMainButton(name) {
  if (name === "Randomize" && phase === "deployment") {
    randomizeFleet(playerFleet, playerBoard, true);
    statusMessage = "Fleet randomized";
  } else if (name === "Reset") {
    resetGame();
  } else if (name === "Start" && phase === "deployment") {
    startBattle();
  } else if (name === "Quit") {
    gameOver = true;
    winner = "Game Over —";
  }
}

function handleMusicButton(name) {
  if (name === "Prev") setTrack(musicIndex - 1);
  if (name === "PlayPause") toggleMusic();
  if (name === "Next") setTrack(musicIndex + 1);
  if (name === "Vol-") {
    musicVolume = Math.max(0, musicVolume - 0.05);
    audio.music.volume = musicVolume;
  }
  if (name === "Vol+") {
    musicVolume = Math.min(1, musicVolume + 0.05);
    audio.music.volume = musicVolume;
  }
}

function handleSfxButton(name) {
  const direction = name.endsWith("VolUp") ? 0.01 : -0.01;
  if (name.startsWith("Splash")) {
    splashVolume = Math.min(1, Math.max(0, splashVolume + direction));
  }
  if (name.startsWith("Explosion")) {
    explosionVolume = Math.min(1, Math.max(0, explosionVolume + direction));
  }
  if (name.startsWith("Gunshot")) {
    gunshotVolume = Math.min(1, Math.max(0, gunshotVolume + direction));
  }
}

canvas.addEventListener("pointerdown", (event) => {
  event.preventDefault();
  pointer = pointFromEvent(event);
  if (!musicStarted) {
    musicStarted = true;
    setTrack(musicIndex);
  }

  if (gameOver) {
    const restart = { x: WIDTH / 2 - 160, y: HEIGHT / 2 + 50, width: 150, height: 50 };
    const quit = { x: WIDTH / 2 + 10, y: HEIGHT / 2 + 50, width: 150, height: 50 };
    if (contains(restart, pointer)) resetGame();
    if (contains(quit, pointer)) statusMessage = "Close this browser tab to quit";
    return;
  }

  const mainButton = mainButtons.find((button) => contains(button, pointer));
  if (mainButton) {
    handleMainButton(mainButton.name);
    return;
  }

  const musicButton = musicButtons.find((button) => contains(button, pointer));
  if (musicButton) {
    handleMusicButton(musicButton.name);
    return;
  }

  const sfxButton = sfxButtons.find((button) => contains(button, pointer));
  if (sfxButton) {
    handleSfxButton(sfxButton.name);
    return;
  }

  if (
    phase === "battle" &&
    playerTurn &&
    pointer.x >= COMPUTER_GRID.x &&
    pointer.x < COMPUTER_GRID.x + GRID * CELL &&
    pointer.y >= COMPUTER_GRID.y &&
    pointer.y < COMPUTER_GRID.y + GRID * CELL
  ) {
    const column = Math.floor((pointer.x - COMPUTER_GRID.x) / CELL);
    const row = Math.floor((pointer.y - COMPUTER_GRID.y) / CELL);
    const result = fireAt(computerBoard, computerFleet, row, column, playerStats);
    if (result && !checkGameOver()) {
      playerTurn = false;
      window.setTimeout(computerAttack, 2000);
    }
    return;
  }

  if (phase === "deployment") {
    const ship = shipAt(pointer);
    if (ship) {
      clearShipFromBoard(ship, playerBoard);
      ship.placed = false;
      dragging = {
        ship,
        offsetX: pointer.x - shipDrawPosition(ship).x,
        offsetY: pointer.y - shipDrawPosition(ship).y,
      };
      canvas.setPointerCapture(event.pointerId);
    }
  }
});

canvas.addEventListener("pointermove", (event) => {
  pointer = pointFromEvent(event);
  if (!dragging) return;
  dragging.ship.x = pointer.x - dragging.offsetX;
  dragging.ship.y = pointer.y - dragging.offsetY;
});

canvas.addEventListener("pointerup", (event) => {
  if (!dragging) return;
  const ship = dragging.ship;
  const position = shipDrawPosition(ship);
  const centerX = position.x + position.width / 2;
  const centerY = position.y + position.height / 2;
  const column = Math.floor((centerX - PLAYER_GRID.x) / CELL);
  const row = Math.floor((centerY - PLAYER_GRID.y) / CELL);

  if (!placeShip(ship, row, column, playerBoard)) {
    ship.x = ship.start.x;
    ship.y = ship.start.y;
    ship.placed = false;
  }
  dragging = null;
  canvas.releasePointerCapture(event.pointerId);
});

canvas.addEventListener("contextmenu", (event) => {
  event.preventDefault();
  if (phase !== "deployment") return;
  const point = pointFromEvent(event);
  const ship = shipAt(point);
  if (!ship) return;
  const oldHorizontal = ship.horizontal;
  const oldRow = ship.row;
  const oldColumn = ship.column;
  clearShipFromBoard(ship, playerBoard);
  ship.horizontal = !ship.horizontal;
  if (
    ship.placed &&
    oldRow !== null &&
    !placeShip(ship, oldRow, oldColumn, playerBoard)
  ) {
    ship.horizontal = oldHorizontal;
    placeShip(ship, oldRow, oldColumn, playerBoard);
  }
});

preload()
  .then(() => {
    resetGame();
    setTrack(0);
    document.body.classList.add("is-ready");
    render();
  })
  .catch((error) => {
    document.querySelector("#loading").textContent = `Yükleme hatası: ${error.message}`;
  });
