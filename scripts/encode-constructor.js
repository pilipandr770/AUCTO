// scripts/encode-constructor.js
/**
 * Генерація hex-рядка для Constructor Arguments на PolygonScan
 * Використовує ethers.js v6
 */
const { AbiCoder, parseUnits } = require("ethers");

// ——— Налаштуйте ваші значення (ті, що вводили при деплої) ———
const name = "MyToken";                     // _name (string)
const symbol = "MTK";                        // _symbol (string)
const initialSupply = BigInt("1000000");    // _initialSupply (uint256)
const tokenPrice = parseUnits("0.01", "ether"); // _tokenPrice (uint256)
// ————————————————————————————————————————————————

function main() {
  // Масив типів і значень у порядку конструктора
  const types = ["string", "string", "uint256", "uint256"];
  const values = [name, symbol, initialSupply, tokenPrice];

  // ABI-encode і обрізка префіксу
  const encoded = new AbiCoder().encode(types, values).slice(2);
  console.log("Constructor args hex (без 0x):", encoded);
}

main();
