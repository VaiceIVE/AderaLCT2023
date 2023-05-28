const db = require('mongoose')

module.exports = async function() {
    await db.connect(process.env.DB_URL_NONLOCAL, {
        authSource: "admin",
        user: "root",
        pass: "admin",
        useNewUrlParser: true,
        useUnifiedTopology: true,
    });
}