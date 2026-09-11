// Live price calculator on the order page
const boxSel  = document.getElementById("boxSelect");
const qtyIn   = document.getElementById("qtyInput");
const zoneSel = document.getElementById("zoneSelect");
const subEl   = document.getElementById("subtotal");
const delEl   = document.getElementById("delivery");
const totEl   = document.getElementById("total");

// These match the Python dictionaries in app.py — keep them in sync!
const BOX_PRICES = { "6": 80, "12": 150, "18": 200 };
const ZONE_FEES = {
  "roysambu": 100, "kasarani": 150, "zimmerman": 150,
  "kahawa": 200, "thika-road": 200, "eastleigh": 250,
  "westlands": 300, "cbd": 300, "parklands": 300,
  "kilimani": 350, "other": 0
};

function updateQuote() {
  if (!boxSel) return; // not on order page

  const boxPrice = BOX_PRICES[boxSel.value] || 0;
  const qty      = parseInt(qtyIn.value) || 1;
  const zoneFee  = ZONE_FEES[zoneSel.value] || 0;

  const subtotal = boxPrice * qty;
  const total    = subtotal + zoneFee;

  subEl.textContent = "KSH " + subtotal;
  delEl.textContent = "KSH " + zoneFee;
  totEl.textContent = "KSH " + total;
}

if (boxSel) {
  boxSel.addEventListener("change", updateQuote);
  qtyIn.addEventListener("input", updateQuote);
  zoneSel.addEventListener("change", updateQuote);
  updateQuote(); // initial calculation
}