const express = require('express')
require('dotenv').config()
const cors = require('cors')
const swaggerUi = require('swagger-ui-express')
const swaggerFile = require('./Swagger/swagger_output.json')
const StorageRouter = require('./Routers/StorageRouter')


const PORT = process.env.PORT || 8005


const app = express()

app.use(express.static('./Storage/'))
app.use(cors({credentials: true, origin:['http://127.0.0.1:5173']}))
app.use(express.json())


app.use(StorageRouter)
app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerFile))











app.listen(PORT, () => {console.log(`Listening ${PORT}`)})
