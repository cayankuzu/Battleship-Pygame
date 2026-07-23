const gridSize = 10;
const fleetBlueprint = [
  { name: "Uçak gemisi", size: 5 },
  { name: "Zırhlı", size: 4 },
  { name: "Kruvazör", size: 3 },
  { name: "Denizaltı", size: 3 },
  { name: "Muhrip", size: 2 },
];
const totalShipCells = fleetBlueprint.reduce((total, ship) => total + ship.size, 0);

let playerBoard = [];
let enemyBoard = [];
let playerFleet = [];
let enemyFleet = [];
let playerShots = new Set();
let enemyShots = new Set();
let playerHitCount = 0;
let enemyHitCount = 0;
let isPlayerTurn = true;
let gameOver = false;
let logEntries = [];

const enemyGrid = document.querySelector("#enemyGrid");
const playerGrid = document.querySelector("#playerGrid");
const statusElement = document.querySelector("#status");
const playerHitsElement = document.querySelector("#playerHits");
const computerHitsElement = document.querySelector("#computerHits");
const turnLabel = document.querySelector("#turnLabel");
const enemyFleetElement = document.querySelector("#enemyFleet");
const gameLog = document.querySelector("#gameLog");
const resetButton = document.querySelector("#resetButton");

function coordinate(row, column) {
  return `${row}-${column}`;
}

function emptyBoard() {
  return Array.from({ length: gridSize }, () => Array(gridSize).fill(null));
}

function randomInteger(maximum) {
  return Math.floor(Math.random() * maximum);
}

function createFleet(board) {
  return fleetBlueprint.map((blueprint, shipIndex) => {
    let cells = [];
    let placed = false;

    while (!placed) {
      const horizontal = Math.random() > 0.5;
      const row = randomInteger(horizontal ? gridSize : gridSize - blueprint.size + 1);
      const column = randomInteger(horizontal ? gridSize - blueprint.size + 1 : gridSize);
      const candidate = Array.from({ length: blueprint.size }, (_, offset) => ({
        row: row + (horizontal ? 0 : offset),
        column: column + (horizontal ? offset : 0),
      }));

      const hasCollision = candidate.some(({ row: nextRow, column: nextColumn }) => {
        for (let aroundRow = nextRow - 1; aroundRow <= nextRow + 1; aroundRow += 1) {
          for (
            let aroundColumn = nextColumn - 1;
            aroundColumn <= nextColumn + 1;
            aroundColumn += 1
          ) {
            if (board[aroundRow]?.[aroundColumn] !== null && board[aroundRow]?.[aroundColumn] !== undefined) {
              return true;
            }
          }
        }
        return false;
      });

      if (!hasCollision) {
        cells = candidate;
        candidate.forEach(({ row: nextRow, column: nextColumn }) => {
          board[nextRow][nextColumn] = shipIndex;
        });
        placed = true;
      }
    }

    return { ...blueprint, cells, hits: new Set(), sunk: false };
  });
}

function createAxes(panel) {
  const letters = "ABCDEFGHIJ".split("");
  panel.querySelector(".axis-top").innerHTML = Array.from(
    { length: gridSize },
    (_, index) => `<span>${index + 1}</span>`,
  ).join("");
  panel.querySelector(".axis-left").innerHTML = letters.map((letter) => `<span>${letter}</span>`).join("");
}

function renderGrid(element, board, shots, showShips) {
  element.innerHTML = "";

  for (let row = 0; row < gridSize; row += 1) {
    for (let column = 0; column < gridSize; column += 1) {
      const key = coordinate(row, column);
      const shipIndex = board[row][column];
      const wasShot = shots.has(key);
      const cell = document.createElement(showShips ? "span" : "button");
      cell.className = "cell";

      if (!showShips) {
        cell.type = "button";
        cell.setAttribute("aria-label", `${"ABCDEFGHIJ"[row]}${column + 1} koordinatına ateş et`);
        cell.disabled = wasShot || !isPlayerTurn || gameOver;
        cell.addEventListener("click", () => playerFire(row, column));
      }

      if (showShips && shipIndex !== null) cell.classList.add("ship");
      if (wasShot) cell.classList.add(shipIndex !== null ? "hit" : "miss");
      element.appendChild(cell);
    }
  }
}

function renderFleet() {
  enemyFleetElement.innerHTML = enemyFleet
    .map(
      (ship) => `
        <span class="ship-chip ${ship.sunk ? "sunk" : ""}" style="--ship-width:${ship.size * 7}px">
          ${ship.name}
        </span>
      `,
    )
    .join("");
}

function renderLog() {
  gameLog.innerHTML = logEntries
    .slice(0, 5)
    .map((entry) => `<li>${entry}</li>`)
    .join("");
}

function render() {
  renderGrid(enemyGrid, enemyBoard, playerShots, false);
  renderGrid(playerGrid, playerBoard, enemyShots, true);
  renderFleet();
  renderLog();
  playerHitsElement.textContent = `${playerHitCount} / ${totalShipCells}`;
  computerHitsElement.textContent = `${enemyHitCount} / ${totalShipCells}`;
  turnLabel.textContent = gameOver ? "Bitti" : isPlayerTurn ? "Sende" : "Rakipte";
}

function addLog(message) {
  logEntries.unshift(message);
}

function applyShot(board, fleet, shots, row, column) {
  const key = coordinate(row, column);
  shots.add(key);
  const shipIndex = board[row][column];

  if (shipIndex === null) return { hit: false, sunkShip: null };

  const ship = fleet[shipIndex];
  ship.hits.add(key);
  if (ship.hits.size === ship.size) ship.sunk = true;
  return { hit: true, sunkShip: ship.sunk ? ship : null };
}

function coordinateLabel(row, column) {
  return `${"ABCDEFGHIJ"[row]}${column + 1}`;
}

function playerFire(row, column) {
  if (!isPlayerTurn || gameOver || playerShots.has(coordinate(row, column))) return;

  const result = applyShot(enemyBoard, enemyFleet, playerShots, row, column);
  if (result.hit) playerHitCount += 1;

  const target = coordinateLabel(row, column);
  if (result.sunkShip) {
    statusElement.textContent = `${result.sunkShip.name} battı!`;
    addLog(`${target}: İsabet — ${result.sunkShip.name} battı.`);
  } else if (result.hit) {
    statusElement.textContent = `${target}: İsabet!`;
    addLog(`${target}: İsabet.`);
  } else {
    statusElement.textContent = `${target}: Iska. Rakip ateş ediyor.`;
    addLog(`${target}: Iska.`);
  }

  if (playerHitCount === totalShipCells) {
    finishGame(true);
    return;
  }

  isPlayerTurn = false;
  render();
  window.setTimeout(computerFire, 650);
}

function computerFire() {
  if (gameOver) return;

  const available = [];
  for (let row = 0; row < gridSize; row += 1) {
    for (let column = 0; column < gridSize; column += 1) {
      if (!enemyShots.has(coordinate(row, column))) available.push({ row, column });
    }
  }

  const target = available[randomInteger(available.length)];
  const result = applyShot(
    playerBoard,
    playerFleet,
    enemyShots,
    target.row,
    target.column,
  );
  if (result.hit) enemyHitCount += 1;

  const label = coordinateLabel(target.row, target.column);
  if (result.sunkShip) {
    statusElement.textContent = `Rakip ${result.sunkShip.name} gemini batırdı.`;
    addLog(`Rakip ${label}: ${result.sunkShip.name} battı.`);
  } else if (result.hit) {
    statusElement.textContent = `Rakip ${label} koordinatında isabet buldu.`;
    addLog(`Rakip ${label}: İsabet.`);
  } else {
    statusElement.textContent = `Rakip ${label} koordinatını ıskaladı. Sıra sende.`;
    addLog(`Rakip ${label}: Iska.`);
  }

  if (enemyHitCount === totalShipCells) {
    finishGame(false);
    return;
  }

  isPlayerTurn = true;
  render();
}

function finishGame(playerWon) {
  gameOver = true;
  isPlayerTurn = false;
  statusElement.textContent = playerWon
    ? "Düşman filosunu batırdın. Zafer senin!"
    : "Filon battı. Yeni bir muharebede tekrar dene.";
  addLog(playerWon ? "Muharebe kazanıldı." : "Muharebe kaybedildi.");
  render();
}

function resetGame() {
  playerBoard = emptyBoard();
  enemyBoard = emptyBoard();
  playerFleet = createFleet(playerBoard);
  enemyFleet = createFleet(enemyBoard);
  playerShots = new Set();
  enemyShots = new Set();
  playerHitCount = 0;
  enemyHitCount = 0;
  isPlayerTurn = true;
  gameOver = false;
  logEntries = ["Filolar yerleştirildi. İlk atış sende."];
  statusElement.textContent = "Hedef seç.";
  render();
}

document.querySelectorAll(".board-panel").forEach(createAxes);
resetButton.addEventListener("click", resetGame);
resetGame();
