require('dotenv').config()
const express = require('express')
const UserRouter = require('./Routers/UserRouter')
const AnalysisRouter = require('./Routers/AnalysisRouter')
const StorageRouter = require('./Routers/StorageRouter')
const cors = require('cors')
const PORT = process.env.PORT || 8004
const app = express()
app.use(express.json())
app.use(cors({credentials: true, origin: ['http://127.0.0.1:5173', 'http://localhost:5173', process.env.CLIENT_URL]}))

app.use('/users', UserRouter)
app.use('/analysis', AnalysisRouter)
app.use('/storage', StorageRouter)



app.listen(PORT, () => {console.log(`Listening ${PORT}!`)})
