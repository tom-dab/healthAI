const axios = require("axios");
const fs = require("fs");

async function descargarCSV(url, ruta) {
    const response = await axios({
        url,
        method: "GET",
        responseType: "stream"
    });

    const writer = fs.createWriteStream(ruta);

    response.data.pipe(writer);

    return new Promise((resolve, reject) => {
        writer.on("finish", resolve);
        writer.on("error", reject);
    });
}

module.exports = { descargarCSV };
//Descargar dataset