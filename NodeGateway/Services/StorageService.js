const FormData = require('form-data')
const path = require('path')
const axios = require('axios')
const fs = require('fs')
const DownloadFile = require('../Functions/DownloadFile')

class StorageService
{
    async GetFile(filename)
    {
        await DownloadFile(process.env.STORAGE_AGENT_URL + `/file/${filename}`, `Temp/${filename}`)

        return fs.createReadStream(`Temp/${filename}`)
    } 

    async GetAll()
    {
        let res = null
        await axios.get(process.env.STORAGE_AGENT_URL + "/list")
        .then((response) => {res = response.data})
        .catch((err) => {res = err.response.data})
        return res
    } 
}

module.exports = new StorageService()
